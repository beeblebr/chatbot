from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pickle

from datetime import datetime

from pprint import pprint

from collections import defaultdict

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet

from rasa_config import *

from util.sense_utils import transform_topics, perform_batch_call, assemble_topic_wise_rankings, _transform_doc
from util.chat_utils import get_all_topics, get_all_topics_plain
from util.topic_utils import get_top_categories, clean_text

from util.db_utils import *



class ActionSearchKnowledgeBase(Action):
    """Handles intent to search query knowledge base"""

    def name(self):
        return 'action_search_knowledge_base'


    def run(self, dispatcher, tracker, domain):
        message = tracker.latest_message
        nlu_topics = get_all_topics(message)['nlu_topics']
        corpus = list(get_knowledge_corpus())
        server_calls = [] # for batching network requests
        
        for index, k in enumerate(corpus):
            # Fetch separate lists from DB if exists
            k_nlu_topics = k.get('nlu_topics', [])
            k_fallback_topics = k.get('fallback_topics', [])
            # If nlu_topics field not present in DB, extract them from the text
            if not k_nlu_topics:
                k_nlu_topics = get_all_topics_plain(k['text'])['nlu_topics']
                k['topics'] = k_nlu_topics
            # Batch(v.) server calls
            server_calls.append({'topics1': nlu_topics, 'topics2': k_nlu_topics})

        # Perform network request
        similarity_map = perform_batch_call(server_calls)
        
        # Get topic wise ranking
        topic_wise_ranking = assemble_topic_wise_rankings(similarity_map, corpus)


        # Find what topics it matched against so that bot can pose secondary questions back to the user
        matched_variants_count = defaultdict(int)
        for topic in topic_wise_ranking:
            ranking = topic_wise_ranking[topic]

            relevant = filter(lambda x : x['score'] > 0.5, ranking)
            print(topic + ' has ' + str(len(relevant)) + ' entries')

            for variant in map(lambda x : x['matched_variant'], relevant):
                matched_variants_count[variant] += 1

        import operator
        sorted_variant_count = sorted(matched_variants_count.items(), key=operator.itemgetter(1), reverse=True)
        pprint(sorted_variant_count)
        

        dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(top_match['eight_id']))

        return [SlotSet('search_results', ranked)]


class ActionInsertKnowledge(Action):

    def name(self):
        return 'action_insert_knowledge'

    def run(self, dispatcher, tracker, domain):
        message = tracker.latest_message
        text = message.text
        entities = message.entities
        info = filter(lambda x : x['entity'] == 'info', entities)
        
        all_topics = get_all_topics(message)

        k = dict()
        k['timestamp'] = datetime.now()
        k['text'] = text
        k['info'] = info
        k['nlu_topics'] = all_topics['nlu_topics']
        k['fallback_topics'] = all_topics['fallback_topics']

        insert_knowledge(k)
        
        return []
