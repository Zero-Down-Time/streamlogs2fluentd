# Changelog

## 0.9.2
- fixed parser for multi line Lambda events

## 0.9.1
- improved error logging for HTTP requests
- increased timeout / retries to ~204 seconds

## 0.9.0
- TEST mode to be enabled explictly via environment variable
- optional ( enabled by default ) IAM account_id to alias lookup
- minor bugfixes and cleanup
- full CI/CD pipeline using drone.io
- removed AWS online dependencies from tests

## 0.8.6
- added feature to resolve the AWS AccountID to account alias  
  enabled by default, can be disabled via os.env `RESOLVE_ACCOUNT`

## 0.8.5
- initial public release
