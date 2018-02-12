from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pickle
import itertools
import sys
import operator
from collections import defaultdict
from datetime import datetime
from pprint import pprint

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_config import *

from util.sense_utils import perform_batch_call
from util.topic_utils import get_all_topics, prettify_topic, uglify_topic
from util.db_utils import *

from processing import filters, transforms, pipeline


class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base"""

    @staticmethod
    def name():
        return 'action_search_knowledge_base'

    @staticmethod
    def run(dispatcher, tracker, domain):
        user_id = tracker.slots['user_id'].value
        message = tracker.latest_message.text

        add_question_to_user_history(user_id, message)

        # Get topics (noun phrases) for both query and every knowledge item
        query_topics = {
            'text': get_all_topics(message)
        }

        corpus = list(get_knowledge_corpus(exclude_user=user_id))
        corpus_topics_map = [{
            '_id': str(item['_id']),
            'text': get_all_topics(item['transformed_text'], transformed=True)
        } for item in corpus]

        # Fetch custom taxonomy for all topics in `query_topics`
        user_defined_taxonomy = {
            prettify_topic(topic): get_relations(prettify_topic(topic)) for
            topic
            in
            query_topics['text']}

        # Perform network request
        similarity_map, clusters = perform_batch_call({
            'query_topics': query_topics,
            'corpus_topics_map': corpus_topics_map,
            'user_defined_taxonomy': user_defined_taxonomy
        })

        similarity_map = pipeline.execute_pipeline(
            similarity_map,

            (transforms.ConvertSimilarityToFloat,),
            (transforms.ZipWithCorpus, corpus)
        )

        if len(similarity_map) > 1:
            response = {
                'type': 'clarify',
                'specify': [prettify_topic(x[0]) for x in clusters]
            }
        else:
            response = {
                'type': 'found',
                'top_matches': similarity_map
            }
        return [SlotSet('response_metadata', response)]
