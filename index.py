#!/usr/bin/env python
import base64
import requests
import gzip
import json
import msgpack
import struct
import os
import shutil
import re
import logging
import time
import io
import urllib
import datetime
import boto3

__author__ = "Stefan Reimer"
__author_email__ = "stefan@zero-downtime.net"
__version__ = "0.9.5"

# Global alias lookup cache
account_aliases = {}

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)


def boolean(value):
    if value in ('t', 'T', 'true', 'True', 'TRUE', '1', 1, True):
        return True
    return False


def decrypt(encrypted):
    try:
        kms = boto3.client('kms')
        plaintext = kms.decrypt(CiphertextBlob=base64.b64decode(encrypted))['Plaintext']
        return plaintext.decode()
    except Exception:
        logging.exception("Failed to decrypt via KMS")


CHUNK_SIZE = 128
DEBUG = boolean(os.getenv('DEBUG', default=False))
TEST = boolean(os.getenv('TEST', default=False))
RESOLVE_ACCOUNT = boolean(os.getenv('RESOLVE_ACCOUNT', default=True))

if DEBUG:
    logging.getLogger().setLevel(logging.DEBUG)
else:
    logging.getLogger().setLevel(logging.INFO)


# From fluent/fluent-logger-python
class EventTime(msgpack.ExtType):
    def __new__(cls, timestamp):
        seconds = int(timestamp)
        nanoseconds = int(timestamp % 1 * 10 ** 9)
        return super(EventTime, cls).__new__(
            cls,
            code=0,
            data=struct.pack(">II", seconds, nanoseconds),
        )


def fluentd_time(timestamp):
    if isinstance(timestamp, float):
        return EventTime(timestamp)
    else:
        return int(timestamp)


def get_source(region, account_id):
    """ returns a new base source object
        resolves aws account_id to account alias and caches for lifetime of lambda function
    """
    global RESOLVE_ACCOUNT
    source = {'account': account_id, 'region': region}
    if RESOLVE_ACCOUNT and not TEST:
        try:
            if account_id not in account_aliases:
                iam = boto3.client('iam')
                account_aliases[account_id] = iam.list_account_aliases()['AccountAliases'][0]

            source['account_alias'] = account_aliases[account_id]

        except(KeyError, IndexError):
            logger.warning("Could not resolve IAM account alias")
            RESOLVE_ACCOUNT = False
            pass

    return source


class Queue:
    url = urllib.parse.urlsplit(os.getenv('FLUENTD_URL', default=''), scheme='https')
    passwd = os.getenv('FLUENT_SHARED_KEY', default=None)

    verify_certs = os.getenv('FLUENTD_VERIFY_CERTS', default=1)
    if verify_certs in ('f', 'F', 'false', 'False', 'FALSE', '0', 0, False):
        verify_certs = False
    else:
        verify_certs = True

    # cached request session
    request = requests.Session()
    request.headers = {"Content-type": "application/msgpack"}
    if passwd:
        request.auth = ("fluent", passwd)

    def __init__(self, tag):
        self._queue = []
        self.tag = tag
        self.sent = 0

    def send(self, event):
        self._queue.append(event)
        logger.debug("Queued {} event: {}".format(self.tag, event))
        # Send events in chunks
        if len(self._queue) >= CHUNK_SIZE:
            self.flush()

    def flush(self):
        events = len(self._queue)
        if not events:
            return

        logger.debug("Sending {} events to {}/{} ({})".format(events, self.url.geturl(), self.tag, self.request))

        if not TEST:
            # Send events via POSTs reusing the same https connection, retry couple of times
            retries = 0
            _url = '{}/{}'.format(self.url.geturl(), self.tag)
            while True:
                try:
                    r = self.request.post(url=_url, data=msgpack.packb(self._queue), verify=self.verify_certs)
                    if r:
                        break
                    else:
                        logger.warning("HTTP Error: {}".format(r.status_code))

                except requests.RequestException as e:
                    logger.warning("RequestException: {}".format(e))
                    pass

                if retries >= 8:
                    raise Exception("Error sending {} events to {}. Giving up.".format(events, _url))

                retries = retries + 1
                logger.warning("Error sending {} events to {}. Retrying in {} seconds.".format(events, _url, retries**2))
                time.sleep(retries**2)
        else:
            logger.debug("Test mode, dump only: {}".format(msgpack.packb(self._queue)))

        self.sent = self.sent + events
        self._queue = []

    def info(self):
        logger.info("Sent {} events to {}/{} ({})".format(self.sent, self.url.geturl(), self.tag, self.request))


# Handler to handle CloudWatch logs.
def handler(event, context):
    logger.debug("Event received: {}".format(event))

    (region, account_id) = context.invoked_function_arn.split(":")[3:5]

    # Cloudwatch Logs event
    if 'awslogs' in event:
        # Grab the base64-encoded data.
        b64strg = event['awslogs']['data']

        # Decode base64-encoded string, which should be a gzipped object.
        zippedContent = io.BytesIO(base64.b64decode(b64strg))

        # Decompress the content and load JSON.
        with gzip.GzipFile(mode='rb', fileobj=zippedContent) as content:
            for line in content:
                awsLogsData = json.loads(line.decode())

        # First determine type
        if re.match("/aws/lambda/", awsLogsData['logGroup']):
            logs = Queue("aws.lambda")
        elif re.search("cloudtrail", awsLogsData['logGroup'], flags=re.IGNORECASE):
            logs = Queue("aws.cloudtrail")
        elif re.match("RDSOSMetrics", awsLogsData['logGroup']):
            logs = Queue("aws.rdsosmetrics")
        elif re.match("vpcflowlog", awsLogsData['logGroup'], flags=re.IGNORECASE):
            logs = Queue("aws.vpcflowlog")
        else:
            logs = Queue("aws.cloudwatch_logs")

        # Build list of log events
        for e in awsLogsData['logEvents']:
            event = {}
            source = get_source(region, account_id)
            parsed = {}

            # Remove whitespace / empty events & skip over empty events
            e['message'] = e['message'].strip()
            if re.match(r'^\s*$', e['message']):
                continue

            # inject existing data from subscrition filters
            if('extractedFields' in e.keys()):
                for key in e['extractedFields']:
                    event[key] = e['extractedFields'][key]

            # lambda ?
            if logs.tag == 'aws.lambda':
                # First look for the three AWS Lambda entries
                mg = re.match(r'(?P<type>(START|END|REPORT)) RequestId: (?P<request>\S*)', e['message'])
                if mg:
                    parsed['RequestId'] = mg.group('request')
                    if mg.group('type') == 'REPORT':
                        pattern = r'.*(?:\tDuration: (?P<duration>[\d\.\d]+) ms\s*)(?:\tBilled Duration: (?P<billed_duration>[\d\.\d]+) ms\s*)(?:\tMemory Size: (?P<memory_size>[\d\.\d]+) MB\s*)(?:\tMax Memory Used: (?P<max_memory_used>[\d\.\d]+) MB)'

                    elif mg.group('type') == 'START':
                        pattern = r'.*(?:Version: (?P<version>.*))'

                    else:
                        pattern = ''

                    data = re.match(pattern, e['message'])
                    for key in data.groupdict().keys():
                        parsed[key] = data.group(key)

                    # All other info parsed, so just set type itself
                    event['message'] = mg.group('type')

                else:
                    # Try to extract data from AWS default python logging format
                    # This normalizes print vs. logging entries and allows requestid tracking
                    # "[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(message)s\n"
                    _msg = e['message']
                    pattern = r'(?:\[(?P<level>[^\]]*)\]\s)?(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}Z)\s(?P<RequestId>\S*?)\s(?P<message>.*)'
                    data = re.match(pattern, e['message'], flags=re.DOTALL)
                    if data:
                        if data.group('level'):
                            event['level'] = data.group('level')
                        event['time'] = fluentd_time(datetime.datetime.strptime(data.group('time'), '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())
                        parsed['RequestId'] = data.group('RequestId')
                        _msg = data.group('message')

                    # try to parse the remaining as json
                    try:
                        _json = json.loads(_msg)
                        # Make sure we have an actual object assigned to json field
                        if isinstance(_json, dict):
                            event['message_json'] = _json
                        else:
                            event['message'] = _json
                    except (ValueError, TypeError, KeyError):
                        event['message'] = _msg

            # cloudtrail ?
            elif logs.tag == 'aws.cloudtrail':
                try:
                    parsed = json.loads(e['message'])

                    # use eventTime and eventID from the event itself
                    event['time'] = fluentd_time(datetime.datetime.strptime(parsed['eventTime'], '%Y-%m-%dT%H:%M:%SZ').timestamp())
                    event['id'] = parsed['eventID']
                    # override region from cloudtrail event
                    source['region'] = parsed['awsRegion']

                except (ValueError, TypeError, KeyError):
                    event['message'] = e['message']
                    parsed.clear()

            # RDS metrics ?
            elif logs.tag == 'aws.rdsosmetrics':
                try:
                    parsed = json.loads(e['message'])

                except (ValueError, TypeError, KeyError):
                    event['message'] = e['message']

            # VPC FlowLog ?
            # <version> <account-id> <interface-id> <srcaddr> <dstaddr> <srcport> <dstport> <protocol> <packets> <bytes> <start> <end> <action> <log-status>
            elif logs.tag == 'aws.vpcflowlog':
                row = e['message'].split(" ")

                # Skip over NODATA entries, what would be the point having these in ES ?
                if row[13] == 'NODATA':
                    continue

                parsed = {'interface-id': row[2], 'srcaddr': row[3], 'dstaddr': row[4], 'srcport': row[5], 'dstport': row[6], 'protocol': row[7],
                          'packets': row[8], 'bytes': row[9], 'start': row[10], 'end': row[11], 'action': row[12], 'log-status': row[13]}

            # Fallback add raw message
            else:
                event['message'] = e['message']

            if parsed and logs.tag:
                event[logs.tag] = parsed

            # Forward cloudwatch logs event ID
            source['log_group'] = awsLogsData['logGroup']
            source['log_stream'] = awsLogsData['logStream']
            event['source'] = source

            # If time and id are not set yet use data from cloudwatch logs event
            if 'time' not in event:
                event['time'] = fluentd_time(e['timestamp'] / 1000)
            if 'id' not in source:
                event['id'] = e['id']

            logs.send(event)

        logs.flush()
        logs.info()

    # S3 Put event
    elif 'Records' in event:
        s3_client = boto3.client('s3')

        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        file_path = '/tmp/stream2fluentd.gz'
        if TEST:
            shutil.copyfile(key, file_path)
        else:
            s3_client.download_file(bucket, key, file_path)
        source = get_source(region, account_id)
        source['s3_url'] = '{}/{}'.format(bucket, key)

        alb_regex = re.compile(r"(?P<type>[^ ]*) (?P<timestamp>[^ ]*) (?P<elb>[^ ]*) (?P<client_ip>[^ ]*):(?P<client_port>[0-9]*) (?P<target_ip>[^ ]*)[:-](?P<target_port>[0-9]*) (?P<request_processing_time>[-.0-9]*) (?P<target_processing_time>[-.0-9]*) (?P<response_processing_time>[-.0-9]*) (?P<elb_status_code>|[-0-9]*) (?P<target_status_code>-|[-0-9]*) (?P<received_bytes>[-0-9]*) (?P<sent_bytes>[-0-9]*) \"(?P<request_verb>[^ ]*) (?P<request_url>[^ ]*) (?P<request_proto>- |[^ ]*)\" \"(?P<user_agent>[^\"]*)\" (?P<ssl_cipher>[A-Z0-9-]+) (?P<ssl_protocol>[A-Za-z0-9.-]*) (?P<target_group_arn>[^ ]*) \"(?P<trace_id>[^\"]*)\" \"(?P<domain_name>[^\"]*)\" \"(?P<chosen_cert_arn>[^\"]*)\" (?P<matched_rule_priority>[-.0-9]*) (?P<request_creation_time>[^ ]*) \"(?P<actions_executed>[^\"]*)\" \"(?P<redirect_url>[^ ]*)\" \"(?P<error_reason>[^ ]*)\"")

        # try to identify file type by looking at first lines
        with gzip.open(file_path, mode='rt', newline='\n') as data:
            header = data.readlines(2048)

        # ALB Access ?
        if alb_regex.match(header[0]):
            logs = Queue("aws.alb_accesslog")

        # cloudfront access logs
        elif len(header) > 1 and re.match('#Version:', header[0]) and re.match('#Fields:', header[1]):
            logs = Queue("aws.cloudfront_accesslog")

        else:
            logger.warning("{}/{}: Unknown type!".format(bucket, key))
            return

        if logs.tag == 'aws.alb_accesslog':
            with gzip.open(file_path, mode='rt', newline='\n') as data:
                for line in data:
                    event = {}
                    parsed = {}
                    data = alb_regex.match(line)
                    if data:
                        for key in data.groupdict().keys():
                            value = data.group(key)

                            # Remove empty values
                            if value in ['-', '-\n']:
                                continue

                            # Remove times of requests timed out
                            if key in ['request_processing_time', 'target_processing_time', 'response_processing_time'] and value in ['-1']:
                                continue

                            parsed[key] = data.group(key)
                    else:
                        logger.warning("Could not parse ALB access log entry: {}".format(line))
                        continue

                    event['time'] = fluentd_time(datetime.datetime.strptime(parsed['request_creation_time'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())

                    # Copy to host to allow geoip upstream
                    event['host'] = parsed['client_ip']
                    event[logs.tag] = parsed
                    event['source'] = source

                    logs.send(event)

        elif logs.tag == 'aws.cloudfront_accesslog':
            with gzip.open(file_path, mode='rt', newline='\n') as data:
                next(data)
                # columns are in second line: first is #Fields, next two are merged into time later
                columns = next(data).split()[3:]

                for line in data:
                    event = {}
                    parsed = {}

                    # Todo hash each line to create source['id']
                    # source['id'] = md5.of.line matching ES ids

                    row = line.split('\t')
                    # cloudfront events are logged to the second only, date and time are seperate
                    event['time'] = fluentd_time(datetime.datetime.strptime(row[0] + " " + row[1], '%Y-%m-%d %H:%M:%S').timestamp())

                    for n, c in enumerate(columns, 2):
                        value = row[n]
                        if value not in ['-', '-\n']:
                            parsed[c] = row[n]
                            # Copy c-ip to host to allow geoip upstream
                            if c == 'c-ip':
                                event['host'] = row[n]

                    event[logs.tag] = parsed
                    event['source'] = source

                    logs.send(event)

        logs.flush()
        logs.info()
