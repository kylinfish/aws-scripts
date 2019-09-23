import json
import logging
from requests_aws4auth import AWS4Auth
import requests
import boto3


class ESSnapshotWrapper(object):
    """ESSnapshotWrapper
    https://docs.aws.amazon.com/zh_tw/elasticsearch-service/latest/developerguide/es-managedomains-snapshots.html
    """

    def __init__(self, host, region, bucket, role_arn, repository):
        self.host = host
        self.region = region
        self.bucket = bucket
        self.role_arn = role_arn
        self.repository = repository
        self.headers = {"Content-Type": "application/json"}
        self.payload = {
            "type": "s3",
            "settings": {
                "bucket": self.bucket,
                "base_path": self.repository,
                "region": self.region,
                "role_arn": self.role_arn,
            }
        }
        credentials = boto3.Session().get_credentials()
        self.auth = AWS4Auth(credentials.access_key, credentials.secret_key,
                             self.region, "es", session_token=credentials.token)

    def register_repository(self):
        url = self.host + "_snapshot/%s" % (self.repository)

        req = requests.put(url, auth=self.auth, json=self.payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def unregister_repository(self):
        url = self.host + "_snapshot/%s" % (self.repository)

        req = requests.delete(url, auth=self.auth, json=self.payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def take_snapshot(self, snapshot_name, payload=None):
        payload = payload if payload is not None else self.payload

        url = self.host + "_snapshot/%s/%s" % (self.repository, snapshot_name)

        req = requests.put(url, auth=self.auth, json=payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def delete_index(self, index_name):
        url = self.host + index_name

        req = requests.delete(url, auth=self.auth)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def restore_snapshot(self, snapshot_name, payload=None):
        """(one index)"""
        payload = payload if payload is not None else self.payload

        url = self.host + "_snapshot/%s/%s/_restore" % (self.repository, snapshot_name)

        req = requests.post(url, auth=self.auth, json=payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def restore_snapshots(self, snapshot_name):
        """(all indices)"""

        url = self.host + "_snapshot/%s/%s/_restore" % (self.repository, snapshot_name)

        req = requests.post(url, auth=self.auth)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def reindex(self, payload):
        url = self.host + "_reindex"

        req = requests.post(url, auth=self.auth, json=payload)

        logging.info(json.dumps(json.loads(req.text), indent=4))


    def update_alias(self, payload):
        url = self.host + "_aliases"

        req = requests.post(url, auth=self.auth, json=payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))

    def update_settings(self, payload):
        url = self.host + "_cluster/settings"

        req = requests.put(url, auth=self.auth, json=payload, headers=self.headers)

        logging.info(json.dumps(json.loads(req.text), indent=4))
