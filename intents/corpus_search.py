import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from rasa_core.events import SlotSet

from util.db_utils import get_knowledge_corpus, get_relations
from util.topic_utils import get_all_topics, prettify_topic

from processing import pipeline, transforms

from intent import BaseIntent


class CorpusSearch(BaseIntent):


    def __init__(self, tracker, user_id, query):
        BaseIntent.__init__(self, tracker, user_id, query)


    def handle_intent(self):
        query_topics = {'topics': get_all_topics(self.query)}
        corpus = list(get_knowledge_corpus(exclude_user=self.user_id))
        corpus_topics_map = [
            {
                '_id': str(item['_id']),
                'topics': get_all_topics(
                    item['transformed_text'],
                    transformed=True
                )
            }
            for item in corpus]

        user_defined_taxonomy = {
            prettify_topic(topic): get_relations(prettify_topic(topic))
            for topic in query_topics['topics']
        }

        similarity_map, clusters = self.send_corpus_search({
            'query_topics': query_topics,
            'corpus_topics_map': corpus_topics_map,
            'user_defined_taxonomy': user_defined_taxonomy
        })
        if not similarity_map:
            return [
                SlotSet('result', 'NOTHING_FOUND')
            ]
        else:
            similarity_map = pipeline.execute_pipeline(
                similarity_map,
                (transforms.ConvertSimilarityToFloat,),
                (transforms.ZipWithCorpus, corpus)
            )

            if len(similarity_map) > 1:
                logger.info('Corpus clarification needed')
                return [
                    SlotSet('result', 'CORPUS_CLARIFICATION_NEEDED'),
                    SlotSet('intent', 'CORPUS_CLARIFICATION'),
                    SlotSet('similarity_map', similarity_map),
                    SlotSet('clusters', clusters)
                ]
            else:
                logger.info('Corpus result found')
                return [
                    SlotSet('result', 'FOUND'),
                    SlotSet('similarity_map', similarity_map)
                ]


    def send_corpus_search(self, params):
        response = self._make_request(params)
        search_results = json.loads(response['results'])
        clusters = json.loads(response['clusters'])
        return search_results, clusters


    @property
    def intent_name(self):
        return 'CORPUS_SEARCH'
