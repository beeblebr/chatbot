from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet

from rasa_utils import TrackerWrapper

from intents.corpus_clarification import CorpusClarification
from intents.corpus_search import CorpusSearch
from intents.query import Query
from intents.query_clarification import QueryClarification


class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base."""

    @staticmethod
    def name():
        return 'action_search_knowledge_base'

    @staticmethod
    def run(dispatcher, tracker, domain):
        slots_ = tracker.slots
        tracker.slots = TrackerWrapper(slots_)

        user_id = tracker.slots['user_id']
        intent = tracker.slots['intent']
        query = tracker.slots['query']

        intents = {
            'QUERY': Query,
            'QUERY_CLARIFICATION': QueryClarification,
            'CORPUS_SEARCH': CorpusSearch,
            'CORPUS_CLARIFICATION': CorpusClarification
        }
        slot_set = intents[intent](tracker, user_id, query).run()
        # Wrap returned slots in response_metadata
        response_metadata = dict()
        for slot in slot_set:
            response_metadata[slot.key] = slot.value
        logger.info(response_metadata)
        return [SlotSet('response_metadata', response_metadata)]
