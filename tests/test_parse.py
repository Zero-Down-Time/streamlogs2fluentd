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
    event = json.loads('{"awslogs": {"data": "H4sICILSAl0AA3Rlc3QArVNdb9tGEHzvr7gSfWgB09z7vuObHDOuCpsqKAZoawnGkTy5RChSJY9N0iD/vSslLew2BlykLwSxu9idmZt5H+39NLl7X747+CiNLhfl4u4mW68XV1l0Fg1vej9imTIupNLGAmVY7ob7q3GYD9hJ3Jsp6dy+alwS/BTi3dzXoR36j2PrMHq3xzkG1CbAE8qT22+uF2W2LresrirHgVPhjagtOLPbWa00B23BUIkrprma6rE9HDe+bLvgxylKb6MX3TA3F75v/Hh3c78P0fZ0Lfvd9+E48D5qGzzKhWIMJAjJubVCAWgtlJLGaMmUEUpaC0IwARKPWsus5oIKgYdDi8IEt0eOVEomQQmOy8zZX4Lh+kVdD3Mf2iYlDwXa9NGHsy9DIJ+JoHiVkx9WF2SVk/L7IltcEiqAa4VfvCE4I7fhV3yBJj4hTYne/g/o1DPR3S7zl6vtJhzfPgYeU15SmwqdUnXOmP4FO05UNegq9sL6WNQUYsu9iiuEpAWvtdF6E9zhcN4Nrrn76DOyG4c9mXiaJBOv5vq1D8lD/R/7MKmHftfef5a2lpodoQOj1OJBJqnmilrKjZW4EJSmqAhVlINU/AnauMM+op0Vxar4m7c68dYpQCr5OQdA3sY606D1YwM7HgvXNLFzsIsVBTBm58EJ5F1k19linZHTvpRs+vnQuODJ6DvvJj8ln35Ii0F4m276cnS1r1z9mny7H6aAgzUGgtSu60jnpvDdvzWQQA1XqJwSRmlJgTF6RMHQEJYpqpg1EsCiKFZrgCc0MALgUTSuj278maBB82V+RRY5WebrcpG/yL4m2U/LEoufexIJDP3LjeRSCkXx+Q1DhdHOGAoNGijnWgqBdmQY1KdygnAePUmWX5LC/zbj4BLT+izbfTm6p3LyT3RF9uOqKP8zwHA5j+5ocZynhp5LRfbTJly0Xecb8qDJALBDNuHG74fxHVm3f3gs4/zNBRbdW/Kp8WryeNzqU/0owPbDV38Ce70icCIGAAA=" } }')
    index.handler(event, context)

    # {"messageType":"DATA_MESSAGE","owner":"123456789012","logGroup":"vpcflowlog","logStream":"eni-123","subscriptionFilters":["CloudBender_Mgmt"],"logEvents":[{"id":"34622050453399460077466588752684659904424057309929734144","timestamp":1552506436228,"message":"2 747836459185 eni-033856bc201b3773b 10.10.0.227 10.3.9.111 443 52866 6 2 135 1563806853 1563806911 ACCEPT OK"},{"id":"34622050453399460077466588752684659904424057309929734144","timestamp":1552506436228,"message":"2 747836459185 eni-033856bc201b3773b 10.10.9.48 10.10.0.227 24224 17234 6 10 1947 1563827256 1563827316 ACCEPT OK"}]}
    event = json.loads('{"awslogs": {"data": "H4sIAHN1N10AA82R3UoDMRCF732KkOu6JPOXpHe1rr2QotDeiUh/Ylno7pbdrSLFd3eqFPQNhFwczkzOzMecbJ37frXLy49DtmN7O1lOXublYjGZlXZk2/cmd2p7QGIJMTkPau/b3axrjwetvB02r/v2XZ0ffzF0eVVrITfVtX5Ttz+u+01XHYaqbe6q/ZC73o6f7HTfHrc3udnm7mW+qwf7/B1QvuVmODecbLXVHCQBcOyIEVMicS4EEuEYA4NEEk7JEQE5DuhSghSQPJEOHiqFG1a17umZgZ0QalgcXaA1HkygEFGIk49szls7xMiy3oDzawwB18a7Qp8rAMJZY5EK770hQsMQRYwYMB7ZeBaMTiLjRSbtm0yn5ePSPNzbz9G/o0oFxT+AQABkfNCTK5d3xicKPzgQgOUi0ctvsufPqy8JYO/9TQIAAA==" } }')
    index.handler(event, context)

    # Cloudfront Access Logs via S3
    event = json.loads('{ "Records": [ { "eventVersion": "2.0", "eventTime": "1970-01-01T00:00:00.000Z", "requestParameters": { "sourceIPAddress": "127.0.0.1" }, "s3": { "configurationId": "testConfigRule", "object": { "eTag": "0123456789abcdef0123456789abcdef", "sequencer": "0A1B2C3D4E5F678901", "key": "tests/test_cloudfront.gz", "size": 1024 }, "bucket": { "arn": "arn:aws:s3:::mybucket", "name": "file://", "ownerIdentity": { "principalId": "EXAMPLE" } }, "s3SchemaVersion": "1.0" }, "responseElements": { "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH", "x-amz-request-id": "EXAMPLE123456789" }, "awsRegion": "us-east-1", "eventName": "ObjectCreated:Put", "userIdentity": { "principalId": "EXAMPLE" }, "eventSource": "aws:s3" } ] }')
    index.handler(event, context)

    # alb Access Logs via S3
    event = json.loads('{ "Records": [ { "eventVersion": "2.0", "eventTime": "1970-01-01T00:00:00.000Z", "requestParameters": { "sourceIPAddress": "127.0.0.1" }, "s3": { "configurationId": "testConfigRule", "object": { "eTag": "0123456789abcdef0123456789abcdef", "sequencer": "0A1B2C3D4E5F678901", "key": "tests/test_alb_accesslogs.gz", "size": 1024 }, "bucket": { "arn": "arn:aws:s3:::mybucket", "name": "file://", "ownerIdentity": { "principalId": "EXAMPLE" } }, "s3SchemaVersion": "1.0" }, "responseElements": { "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH", "x-amz-request-id": "EXAMPLE123456789" }, "awsRegion": "us-east-1", "eventName": "ObjectCreated:Put", "userIdentity": { "principalId": "EXAMPLE" }, "eventSource": "aws:s3" } ] }')
    index.handler(event, context)

    # unknown file
    event = json.loads('{ "Records": [ { "eventVersion": "2.0", "eventTime": "1970-01-01T00:00:00.000Z", "requestParameters": { "sourceIPAddress": "127.0.0.1" }, "s3": { "configurationId": "testConfigRule", "object": { "eTag": "0123456789abcdef0123456789abcdef", "sequencer": "0A1B2C3D4E5F678901", "key": "tests/test_s3_unknown.gz", "size": 1024 }, "bucket": { "arn": "arn:aws:s3:::mybucket", "name": "file://", "ownerIdentity": { "principalId": "EXAMPLE" } }, "s3SchemaVersion": "1.0" }, "responseElements": { "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH", "x-amz-request-id": "EXAMPLE123456789" }, "awsRegion": "us-east-1", "eventName": "ObjectCreated:Put", "userIdentity": { "principalId": "EXAMPLE" }, "eventSource": "aws:s3" } ] }')
    index.handler(event, context)
