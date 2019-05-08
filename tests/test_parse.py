#!/usr/bin/env python

import os
import sys
import logging
import json

import index
from .utils import FakeLambdaContext

# First allow relative imports in main
foo_dir = os.path.dirname(os.path.join(os.getcwd(), __file__))
sys.path.append(os.path.normpath(os.path.join(foo_dir, '..')))

context = FakeLambdaContext()

logger = logging.getLogger(__name__)
logging.getLogger().setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)

logging.getLogger("index").addHandler(ch)
logging.getLogger("index").setLevel(logging.DEBUG)


def test_parse():
    # Test Cloudwatch Logs
    event = json.loads('{"awslogs": {"data": "H4sICAW8uVwAA3RtcACtU11v00AQfOdXHBaPTb33fZc3p3FLEHFQ4kpAElW2cwkWSRzsM6VU/e9sWpBS1EhF5eUedlczs7Nzt8HGNU22cunNzgXdoB+l0dUwnkyiizg4CarrrauxTBkXUmljgTIsr6vVRV21O+yE2XUTrrNNvshC7xrfWbbbwpfV9mFs4muXbXCOAbUh8JDycPrmfZTGk3TOijzPOHAqnBGFhcwsl1YrzUFbMFQiRNPmTVGXuz3iebn2rm6C7jQ4W1ftoue2C1dfDVcbH8zv2eLvbuv3A7dBuUBSLhRjIEFIzq0VCkBroZQ0RkumjFDSWhCCCZBIai2zmgsqBBL7Eo3x2QZ3pFIyCUpwBDMnfwxD+Kgoqnbry0WXHBo02wZ3Jy9TIJ+pYHyZkHejHhklJH07jqM+oQK4Vvgih+CMTP0XvMCic6+0S/T8P6hTz1Q3HSTno/nM72/fAd6hPKW2K3SXqlPG9GfsZCIvQOcdJ6zriIJCx3KnOjlK0oIX2mg989lud7qussXVQ87Isq42pOHdMGx43hZfnQ8P/X+cw7Cotsty9eTaWmq2lw6MUouETFLNFbWUGysREJSm6AhVlINU/MjaiGEP136KSgI1XKFAJYzSkgJjiArA0HfLFFXMGglgkdtqDXCEygiARwl8vz/6J4I5SAbJBYkSMkgmaZScxa9J/HGQYvFpOQxjwo3kUgpF0WXDcBFMDWZPgwbKuZZC4NUZ/odjcUQ5jzaPkz4Zu28tDg7wUzzrui9XdyyOf6sbxx9G4/SfBfp+W2f7JOE8NfRUKrJpZr5XrtduQQ6aDAA7ZOaHblPVN2RS/nRYxvlhD4vZD/K7cdk4JLf6vr43YH736hfQoJlgiQUAAA==" } }')
    index.handler(event, context)

    # Cloudfront Access Logs via S3
    event = json.loads('{ "Records": [ { "eventVersion": "2.0", "eventTime": "1970-01-01T00:00:00.000Z", "requestParameters": { "sourceIPAddress": "127.0.0.1" }, "s3": { "configurationId": "testConfigRule", "object": { "eTag": "0123456789abcdef0123456789abcdef", "sequencer": "0A1B2C3D4E5F678901", "key": "tests/test_cloudfront.gz", "size": 1024 }, "bucket": { "arn": "arn:aws:s3:::mybucket", "name": "file://", "ownerIdentity": { "principalId": "EXAMPLE" } }, "s3SchemaVersion": "1.0" }, "responseElements": { "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH", "x-amz-request-id": "EXAMPLE123456789" }, "awsRegion": "us-east-1", "eventName": "ObjectCreated:Put", "userIdentity": { "principalId": "EXAMPLE" }, "eventSource": "aws:s3" } ] }')
    index.handler(event, context)

    # alb Access Logs via S3
    event = json.loads('{ "Records": [ { "eventVersion": "2.0", "eventTime": "1970-01-01T00:00:00.000Z", "requestParameters": { "sourceIPAddress": "127.0.0.1" }, "s3": { "configurationId": "testConfigRule", "object": { "eTag": "0123456789abcdef0123456789abcdef", "sequencer": "0A1B2C3D4E5F678901", "key": "tests/test_alb_accesslogs.gz", "size": 1024 }, "bucket": { "arn": "arn:aws:s3:::mybucket", "name": "file://", "ownerIdentity": { "principalId": "EXAMPLE" } }, "s3SchemaVersion": "1.0" }, "responseElements": { "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH", "x-amz-request-id": "EXAMPLE123456789" }, "awsRegion": "us-east-1", "eventName": "ObjectCreated:Put", "userIdentity": { "principalId": "EXAMPLE" }, "eventSource": "aws:s3" } ] }')
    index.handler(event, context)
