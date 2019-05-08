[![Build Status](https://drone.zero-downtime.net/api/badges/ZeroDownTime/streamlogs2fluentd/status.svg)](https://drone.zero-downtime.net/ZeroDownTime/streamlogs2fluentd)

# streamlogs2fluentd

# About
Lambda function to parse and forward log events from various AWS sources to Fluentd.

# Features
- sends events to upstream fluentd encoded as msg_pack to a http_in endpoint
- sends events in chunks up to 128 events

Example Fluentd endpoint config:

```
<source>
  @type http
</source>
```

# Available parsers

## CloudWatch Logs

### Lambda

### Cloudtrail

### RDS metrics

## S3

### Cloudfront Access Logs

### ALB Access Logs

