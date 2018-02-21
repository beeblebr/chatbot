from rasa_core.events import SlotSet

from util.topic_utils import uglify_topic

from intent import BaseIntent
from intents.corpus_search import CorpusSearch

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryClarification(BaseIntent):


    def handle_intent(self):
        logger.info(self.tracker.slots)
        query_topics = self.tracker.slots['query_topics']
        query_clarifications = self.tracker.slots['query_clarifications']
        query_clarifications = self.uglify_clarifications(query_clarifications)
        logger.info('query_topics: %s', tuple(query_topics))
        logger.info('query_clarifications: %s', tuple(query_clarifications.keys()))
        response = self.send_query_clarification(query_topics, query_clarifications)
        if response['result'] == 'QUERY_CLARIFICATION_NEEDED':
            logger.info('Query clarification needed')
            return [
                SlotSet('result', 'QUERY_CLARIFICATION_NEEDED'),
                SlotSet('intent', 'QUERY_CLARIFICATION'),
                SlotSet(
                    'query_clarifications',
                    response['query_clarifications']
                ),
                SlotSet(
                    'query_topics',
                    response['query_topics']
                )
            ]
        elif response['result'] == 'QUERY_SUCCESS':
            logger.info('Query success')
            return CorpusSearch(self.tracker, self.user_id, None).handle_intent()

    def uglify_clarifications(self, query_clarifications):
        for ambiguous_phrase in query_clarifications:
            # Assume only one option is selected
            selected_option = query_clarifications[ambiguous_phrase][0]
            if '+' in selected_option:
                options = map(uglify_topic, selected_option.split(' + '))
            else:
                options = [uglify_topic(selected_option)]
            query_clarifications[ambiguous_phrase] = options
        return query_clarifications

    def send_query_clarification(self, query_topics, query_clarifications):
        response = self._make_request({
            'query_topics': query_topics,
            'query_clarifications': query_clarifications
        })
        logger.info(response)
        return response

    @property
    def intent_name(self):
        return 'QUERY_CLARIFICATION'
