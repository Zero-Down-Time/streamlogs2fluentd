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
    event = json.loads('{"awslogs": {"data": "H4sIAGPPdF4AA+VUTW/bRhC991dshR5awBRnv3cJ9CDHjKvClgOJAdpahrAkVwoRilTJZRI3yH/v0HYCu7ULF82tF4KYGcx78+bNfpzsfd+7nc+uD36STE5m2Wxznq5Ws9N0cjRp3ze+wzBlXEiljQXKMFy3u9OuHQ6Yid37Pq7dPi9dHHwfou3QFKFqm9uyVei822MdA2pj4DHl8eV3Z7MsXWVXrMhzx4FT4Y0oLDiz3VqtNAdtwVCJLfoh74uuOowdX1Z18F0/SS4nL+p2KI99U/puc77bh8nVDVr6zjdhLPg4qUoE5UIxBhKE5NxaoQC0FkpJY7RkygglrQUhmACJoNYyq7mgQiBwqFCY4PY4I5WSSVCCYzNz9FkwbD8rinZoQlUm5L5A62by6ei/MZDPZLB8vSA/XxyTiwXJflqmsxNCBXCt8IsYgjNyGd7gBsrohmlC9NVXYKeeye5yvnh5cbUO4+4j4BHlGbWJ0AlVU8b0b5hxIi9A55EX1keioBBZ7lWUIyUteKGN1uvgDodp3bpyc+szsu3aPel5Esc9z4firQ/xff0f+jAu2mZb7R4dW0vNRurAKLUIyCTVXFFLubESG4LSFBWhinKQij8xNvawD8ZOl8uL5Ze51c3cOgFIJJ9yAJzbWGdKtH5kYMsj4coycg62kaIAxmw9OIFzL9OzdLZKyU2/hKyb4VC64Enna+9638d3P6TCQ/iQrJusc4XPXfGWfL9v+4CFBR4EKVxdk9r14Ye/ayCBGq5QOSWM0pICY3RkwdAQlimqmDUSwKIoVmuAJzQwAuDBaZyNbvyVoEEX88UpmS3IfLHKZosX6bck/WWeYfCxlUhg6F9uJJdSKGq0MgwVRjvjUWjQQDnXUgi0I8NDfepOkI593IkMRicyyChNuEnATjlXuBEnvIdtbqKSexmJ3KMTDeURyBHQCMkKvg69D5vO97575zd7v2+7axJawoSawvkxKYauQ73razL0VbMjKOPUYnw31m7euK4kPxKYwudI327DXeQZSuivokS6OCFL//uAhXN8t551gM/Z0z+ze+rF+Cu7ZfrqYpn9a4LhZOjceOxYTw2dSkX2/TocV3XtS3IvyQAwQ9bh/HZ5q+oPj2GsPz/GoPtA7hKve4/gVt/E//cCzJsq3OtCrUKIsdGozNWnb/4EFS89L0YIAAA=" } }')
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
