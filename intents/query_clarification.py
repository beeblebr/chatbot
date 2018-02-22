from rasa_core.events import SlotSet

from util.topic_utils import uglify_topic

from intent import BaseIntent
from intents.corpus_search import CorpusSearch

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryClarification(BaseIntent):

    def handle_intent(self):
        query_topics = self.tracker.slots['query_topics']
        query_clarifications = self.tracker.slots['query_clarifications']
        query_clarifications = self.uglify_clarifications(query_clarifications)
        query_topics = self.update_query_topics_with_clarifications(
            query_topics,
            query_clarifications
        )
        self.tracker.slots['query_topics'] = query_topics
        logger.info(query_topics)
        return CorpusSearch(self.tracker, self.user_id, None).handle_intent()

    def update_query_topics_with_clarifications(self, query_topics, query_clarifications):
        search_topics = []
        for topic in query_topics:
            if topic in query_clarifications:
                search_topics.extend(query_clarifications[topic])
            else:
                search_topics.append(topic)
        return search_topics

    def uglify_clarifications(self, query_clarifications):
        uglified = {}
        for ambiguous_phrase in query_clarifications.keys():
            # Assume only one option is selected
            selected_option = query_clarifications[ambiguous_phrase][0]
            if '+' in selected_option:
                options = map(uglify_topic, selected_option.split(' + '))
            else:
                options = [uglify_topic(selected_option)]
            uglified[uglify_topic(ambiguous_phrase)] = options
        return uglified

    @property
    def intent_name(self):
        return 'QUERY_CLARIFICATION'
