from rasa_core.events import SlotSet

from util.db_utils import get_knowledge_corpus, get_relations
from util.topic_utils import get_all_topics, prettify_topic

from processing import pipeline, transforms

from intent import BaseIntent

import json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorpusSearch(BaseIntent):

    def handle_intent(self):
        query_topics = {'topics': self.tracker.slots['query_topics']}
        logger.info(query_topics)
        corpus = list(get_knowledge_corpus(exclude_user=self.user_id))
        corpus_topics_map = self.get_corpus_topics_map(corpus)
        user_defined_taxonomy = {
            prettify_topic(topic): get_relations(prettify_topic(topic))
            for topic in query_topics
        }

        similarity_map, clusters = self.send_corpus_search({
            'query_topics': query_topics,
            'corpus_topics_map': corpus_topics_map,
            'user_defined_taxonomy': user_defined_taxonomy
        })
        logger.info(clusters)
        if not similarity_map:
            return [
                SlotSet('result', 'NOTHING_FOUND')
            ]

        similarity_map = pipeline.execute_pipeline(
            similarity_map,
            (transforms.ConvertSimilarityToFloat,),
            (transforms.ZipWithCorpus, corpus)
        )
        return self.get_slot_set(similarity_map, clusters)

    def get_slot_set(self, similarity_map, clusters):
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

    def get_corpus_topics_map(self, corpus):
        corpus_topics_map = []
        for item in corpus:
            corpus_topics_map.append({
                '_id': str(item['_id']),
                'topics': get_all_topics(
                    item['transformed_text'],
                    transformed=True
                )
            })
        return corpus_topics_map

    def send_corpus_search(self, params):
        response = self._make_request(params)
        search_results = json.loads(response['results'])
        clusters = json.loads(response['clusters'])
        return search_results, clusters

    @property
    def intent_name(self):
        return 'CORPUS_SEARCH'
