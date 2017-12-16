from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pickle
import itertools
from collections import defaultdict
from datetime import datetime
from pprint import pprint

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_config import *

from util.sense_utils import transform_topics, perform_batch_call, _transform_doc
from util.chat_utils import get_all_topics, get_all_topics_plain
from util.topic_utils import get_top_categories, assemble_topic_wise_rankings, get_aggregate_scores, find_topic_intersection, hashabledict
from util.db_utils import *



class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base"""

    def name(self):
        return 'action_search_knowledge_base'


    def run(self, dispatcher, tracker, domain):
        message = tracker.latest_message
        nlu_topics = get_all_topics(message)['nlu_topics']
        corpus = list(get_knowledge_corpus())
        server_calls = [] # for batching network requests
        
        try:        
            # Perform network request
            import os
            if os.path.exists('similarity_map') and False:
                similarity_map = pickle.load(open('similarity_map', 'rb'))
            else:
                for index, k in enumerate(corpus):
                    k_nlu_topics = get_all_topics_plain(k['text'])['nlu_topics']
                    # Batch(v.) server calls
                    server_calls.append({'topics1': nlu_topics, 'topics2': k_nlu_topics})
                similarity_map = perform_batch_call(server_calls)
                pprint(similarity_map)
                pickle.dump(similarity_map, open('similarity_map', 'wb'))
        except Exception as e:
            print(e)
            raw_input('www>>')

        try:
            # Get topic wise ranking
            topic_wise_ranking = assemble_topic_wise_rankings(similarity_map, corpus)

            # Calculate average similarity scores over all topic perspectives
            aggregate_ranking = get_aggregate_scores(topic_wise_ranking, corpus)
            aggregate_ranking.sort(key=lambda x : x['avg_score'], reverse=True)

            # Topic-wise sorting is deferred until aggregate merging to preserve order
            for topic in topic_wise_ranking:
                topic_wise_ranking[topic].sort(key=lambda x : x['score'], reverse=True)
                # Keep only items that have a similarity score greater than 55%
                topic_wise_ranking[topic] = filter(lambda x : x['score'] > 0.55, topic_wise_ranking[topic])
                print(topic + ' has ' + str(len(topic_wise_ranking[topic])) + ' entries')
        except Exception as e:
            print(e)


        # Get the list of topics along with their ranks (from the server response)
        topics = []
        for topic in similarity_map[0]:
            topic = topic.copy()
            topics.append(topic)

        try:
            # Find the intersection of the most number of topics, and prioritize the combination with most rarity (within the given number of topics)
            common_items = []
            for size in range(len(topics), 0, -1):
                # Get all combinations of topics of length `size` 
                n_sized_combinations = map(list, list(itertools.combinations(topics, size)))
                # The metric for rarity is the sum of Sense2Vec ranks of all topics in the combination
                n_sized_combinations.sort(key=lambda comb : sum([x['rank'] for x in comb]))

                # Iterate in decreasing order of rarity
                for combination in n_sized_combinations:
                    combination_names = map(lambda x : x['topic'], combination)
                    common_items = find_topic_intersection(combination_names, topic_wise_ranking)
                    common_items.sort(key=lambda x : x['score'], reverse=True)
                    if common_items:
                        # print(combination)
                        # raw_input('>>>1')
                        # print('\n')
                        # pprint(common_items[0])
                        # print('arising out of')
                        # print(combination_names)
                        # print('\n')
                        break
                else:
                    # Reduce combination size by 1 and continue
                    continue
                break
            else:
                dispatcher.utter_template('utter_nothing_found')
                response = {'type': 'nothing_found'}
                return [SlotSet('response_metadata', response)]
            
            prettify_tag = lambda x : '"' + ' '.join(x.split('|')[0].split('_')) + '"'
            if common_items:
                # Extract topic names from the dicts containing ranks
                combination = map(lambda x : x['topic'], combination)
                topics = map(lambda x : x['topic'], topics)

                present_tags = map(prettify_tag, combination)
                absent_tags = map(prettify_tag, list(set(topics) - set(combination)))

                if not absent_tags:
                    dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(common_items[0]['eight_id']))
                    response = {'type': 'found', 'top_matches': common_items}

                dispatcher.utter_template('utter_compromise', present_tags=', '.join(present_tags), absent_tags=', '.join(absent_tags))
                dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(common_items[0]['eight_id']))

                response = {'type': 'compromise', 'top_matches': common_items}

                return [SlotSet('response_metadata', response)]

        except Exception as e:
            print(e)


        # Find what topics it matched against so that bot can pose secondary questions back to the user
        matched_variants_count = defaultdict(int)
        for topic in topic_wise_ranking:
            for variant in map(lambda x : x['matched_variant'], relevant):
                matched_variants_count[variant] += 1

        sorted_variant_count = sorted(matched_variants_count.items(), key=operator.itemgetter(1), reverse=True)
        pprint(sorted_variant_count)
        pickle.dump(sorted_variant_count, open('cluster', 'wb'))

        dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(top_match['eight_id']))

        return [SlotSet('search_results', ranked)]


class ActionInsertKnowledge(Action):

    def name(self):
        return 'action_insert_knowledge'

    def run(self, dispatcher, tracker, domain):
        message = tracker.latest_message
        text = message.text

        k = dict()
        k['timestamp'] = datetime.now()
        k['text'] = text

        insert_knowledge(k)
        
        return []
