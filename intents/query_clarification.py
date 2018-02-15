import json

from intent import BaseIntent


class QueryClarification(BaseIntent):


    def __init__(self, tracker, user_id, query):
        BaseIntent.__init__(tracker, user_id, query)


    def run(self):
        pass


    @property
    def intent_name(self):
        return 'QUERY_CLARIFICATION'
