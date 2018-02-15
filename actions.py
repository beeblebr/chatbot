from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core.actions.action import Action

from intents.corpus_clarification import CorpusClarification
from intents.corpus_search import CorpusSearch
from intents.query import Query
from intents.query_clarification import QueryClarification


class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base"""

    @staticmethod
    def name():
        return 'action_search_knowledge_base'

    @staticmethod
    def run(dispatcher, tracker, domain):
        user_id = tracker.slots['user_id'].value
        intent = tracker.slots['intent'].value
        query = tracker.slots['query'].value

        intents = {
            'QUERY': Query,
            'QUERY_CLARIFICATION': QueryClarification,
            'CORPUS_SEARCH': CorpusSearch,
            'CORPUS_CLARIFICATION': CorpusClarification
        }
        slot_set = intents[intent](tracker, user_id, query)
        return slot_set
