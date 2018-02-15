from abc import abstractmethod

import json
import requests

import conf


class BaseIntent(object):

    def __init__(self, tracker, user_id, query):
        self.tracker = tracker
        self.user_id = user_id
        self.query = query

    @abstractmethod
    def intent_name(self):
        raise NotImplementedError()

    @abstractmethod
    def run(self):
        raise NotImplementedError()

    def endpoint(self):
        return '/'

    def _make_request(self, data):
        headers = {'content-type': 'application/json'}
        data['intent'] = self.intent_name()
        response = requests.post(
            conf.SENSE_SERVER_URL + self.endpoint(),
            data=json.dumps(data),
            headers=headers
        ).json()
        return response
