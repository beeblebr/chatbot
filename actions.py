from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet

from rasa_utils import TrackerWrapper

from intents.corpus_clarification import CorpusClarification
from intents.corpus_search import CorpusSearch
from intents.query import Query
from intents.query_clarification import QueryClarification

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base."""

    @staticmethod
    def name():
        return 'action_search_knowledge_base'

    @staticmethod
    def run(dispatcher, tracker, domain):
        slots_ = tracker.slots
        logger.info('sluts: %s', tracker.slots)
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
        slot_set = intents[intent](tracker, user_id, query).handle_intent()
        # Wrap returned slots in new_response_metadata
        new_response_metadata = {
            slot.key: slot.value for slot in slot_set
        }
        logger.info('new_response_metadata: %s', new_response_metadata)
        # Revert tracker.slots object to original value
        tracker.slots = slots_
        # Update the response_metadata in slots
        response_metadata = tracker.slots['response_metadata'].value
        logger.info('old_response_metadata: %s', response_metadata)
        response_metadata.update(new_response_metadata)
        logger.info('updated_response_metadata: %s', response_metadata)
        return [SlotSet('response_metadata', response_metadata)]
