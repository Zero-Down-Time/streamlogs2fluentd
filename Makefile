VERSION ?= $(shell grep '__version__' index.py | cut -d' ' -f3 | cut -d'-' -f1 | sed -e 's/"//g')
S3_BUCKETS ?= zero-downtime zero-downtime.us-west-2 zero-downtime.eu-central-1 zero-downtime.ap-southeast-2 zero-downtime.us-west-1
S3_PREFIX ?= cloudbender/streamlogs2fluentd

PACKAGE_NAME = streamlogs2fluentd
PACKAGE := $(PACKAGE_NAME)-$(VERSION).zip
PACKAGE_FILE := dist/$(PACKAGE)

.PHONY: test clean build all upload clean_s3

all: test build

test:
	flake8 --ignore=E501 index.py tests
	TEST=True pytest --log-cli-level=DEBUG

clean:
	rm -rf __pycache__ .cache .coverage .pytest_cache dist prof

build: $(PACKAGE_FILE)

$(PACKAGE_FILE):
	rm -rf dist && mkdir dist
	cp -r index.py dist/
	pip install --target dist --no-compile msgpack requests
	cd dist && zip -q -r $(PACKAGE) *

upload: $(PACKAGE_FILE)
	for bucket in $(S3_BUCKETS); do \
	  aws s3 cp --acl public-read $(PACKAGE_FILE) s3://$$bucket/$(S3_PREFIX)/latest.zip; \
	  aws s3 cp --acl public-read $(PACKAGE_FILE) s3://$$bucket/$(S3_PREFIX)/$(PACKAGE); \
	done

clean_s3:
	for bucket in $(S3_BUCKETS); do \
	  aws s3 rm --recursive --exclude "*" --include latest.zip --include $(PACKAGE_NAME)-*.zip s3://$$bucket/$(S3_PREFIX); \
	done
