import json

from util.db_utils import add_question_to_user_history
from util.topic_utils import get_all_topics

from intent import BaseIntent

from intents.corpus_search import CorpusSearch


class Query(BaseIntent):


    def __init__(self, tracker, user_id, query):
        BaseIntent.__init__(tracker, user_id, query)


    def run(self):
        add_question_to_user_history(self.user_id, self.query)
        query_topics = {
            'topics': get_all_topics(self.query)
        }
        result = self.send_query(query_topics)
        if result['result'] == 'QUERY_CLARIFICATION_NEEDED':
            response = {
                'query_clarification_options': result['query_clarification_options']
            }
            return [
                SlotSet('result', 'QUERY_CLARIFICATION_NEEDED'),
                SlotSet('intent', 'QUERY_CLARIFICATION'),
                SlotSet('response_metadata', response)
            ]
        elif result['result'] == 'QUERY_SUCCESS':
            return CorpusSearch(self.tracker, self.user_id, self.query).run()


    def send_query(self, query_topics):
        self._make_request(self.query_topics)
        result = json.loads(response['result'])
        return result


    @property
    def intent_name(self):
        return 'QUERY'
