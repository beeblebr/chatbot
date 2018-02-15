from intent import BaseIntent

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusClarification(BaseIntent):


    def __init__(self, tracker, user_id, query):
        BaseIntent.__init__(self, tracker, user_id, query)


    def handle_intent(self):
        pass


    @property
    def intent_name(self):
        return 'CORPUS_CLARIFICATION'
