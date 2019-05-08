import json
import logging
from cfnlambda import validate_response_data, Status

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

BaseEvent = {
    "StackId": "arn:aws:cloudformation:us-west-2:123456789:stack/test_stack_name/guid",
    "ResponseURL": "http://pre-signed-S3-url-for-response",
    "ResourceType": "Custom::TestResource",
    "RequestId": "unique id for this create request",
    "LogicalResourceId": "MyTestResource"
}


class FakeLambdaContext(object):
    def __init__(self, name='Fake', version='LATEST'):
        self.name = name
        self.version = version
        self.response_body = None

    @property
    def get_remaining_time_in_millis(self):
        return 10000

    @property
    def function_name(self):
        return self.name

    @property
    def function_version(self):
        return self.version

    @property
    def invoked_function_arn(self):
        return 'arn:aws:lambda:us-west-2:231435876663:function:' + self.name

    @property
    def memory_limit_in_mb(self):
        return 1024

    @property
    def aws_request_id(self):
        return '1234567890'

    @property
    def log_stream_name(self):
        return 'ReallyFakeLogStream'


# Copied from cfn_lambda for cmdline tests
# Does NOT actually try issue a request
def mocked_cfn_response(event, context, response_status, response_data={}, physical_resource_id=None):

    if physical_resource_id is None:
        physical_resource_id = context.log_stream_name
    response_data = validate_response_data(response_data)
    reason = ("See the details in CloudWatch Log Stream: %s" %
              context.log_stream_name)
    if (response_status == Status.FAILED) and 'result' in response_data:
        reason = "%s %s" % (response_data['result'], reason)

    body = {
        "Status": response_status,
        "Reason": reason,
        "PhysicalResourceId": physical_resource_id,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    }
    response_body = json.dumps(body)
    logger.info("CFN_RESPONSE would be: %s", response_body)

    context.response_body = body
