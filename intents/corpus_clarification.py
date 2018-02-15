from intent import BaseIntent

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusClarification(BaseIntent):


    def handle_intent(self):
        pass


    @property
    def intent_name(self):
        return 'CORPUS_CLARIFICATION'
