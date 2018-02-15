import json

from intent import BaseIntent


class CorpusClarification(BaseIntent):


    def __init__(self, tracker, user_id, query):
        BaseIntent.__init__(self, tracker, user_id, query)


    @property
    def intent_name(self):
        return 'CORPUS_CLARIFICATION'
