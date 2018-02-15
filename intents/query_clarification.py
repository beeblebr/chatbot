import json

from intent import BaseIntent


class QueryClarification(BaseIntent):


    def handle_intent(self):
        pass


    @property
    def intent_name(self):
        return 'QUERY_CLARIFICATION'
