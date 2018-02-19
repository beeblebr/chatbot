import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from rasa_core.events import SlotSet

from util.db_utils import add_question_to_user_history
from util.topic_utils import get_all_topics

from intent import BaseIntent

from intents.corpus_search import CorpusSearch


class Query(BaseIntent):


    def handle_intent(self):
        add_question_to_user_history(self.user_id, self.query)
        query_topics = {
            'topics': get_all_topics(self.query)
        }
        response = self.send_query(query_topics)
        if response['result'] == 'QUERY_CLARIFICATION_NEEDED':
            logger.info('Query clarification needed')
            return [
                SlotSet('result', 'QUERY_CLARIFICATION_NEEDED'),
                SlotSet('intent', 'QUERY_CLARIFICATION'),
                SlotSet(
                    'query_clarifications',
                    response['query_clarifications']
                )
            ]
        elif response['result'] == 'QUERY_SUCCESS':
            logger.info('Query success')
            return CorpusSearch(self.tracker, self.user_id, self.query).handle_intent()


    def send_query(self, query_topics):
        response = self._make_request(query_topics)
        logger.info(response)
        return response


    @property
    def intent_name(self):
        return 'QUERY'
