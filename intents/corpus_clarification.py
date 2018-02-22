from intent import BaseIntent

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusClarification(BaseIntent):

    def handle_intent(self):
        relevant_knowledge_items = self.tracker.slots['relevant_knowledge_items']
        relevant_ki_topics = map(
            lambda item: item['ki_topics'],
            relevant_knowledge_items
        )
        response = self._make_request(relevant_ki_topics)
        if response['result'] == 'CORPUS_CLARIFICATION_NEEDED':
            pass
        elif response['result'] == 'FOUND':
            pass

    @property
    def intent_name(self):
        return 'CORPUS_CLARIFICATION'
