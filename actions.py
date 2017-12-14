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
from util.topic_utils import get_top_categories, assemble_topic_wise_rankings, get_aggregate_scores, find_topic_intersection
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
            k_nlu_topics = get_all_topics_plain(k['text'])['nlu_topics']
            # Batch(v.) server calls
            server_calls.append({'topics1': nlu_topics, 'topics2': k_nlu_topics})
        # Perform network request
        similarity_map = perform_batch_call(server_calls)

        topics = []
        for topic in similarity_map[0]:
            topic = topic.copy()
            topic.pop('matched_variant')
            topic.pop('score')
            topics.append(topic)
        
        try:
            # Get topic wise ranking
            topic_wise_ranking = assemble_topic_wise_rankings(similarity_map, corpus)

            # Calculate average similarity scores over all topic perspectives
            aggregate_ranking = get_aggregate_scores(topic_wise_ranking, corpus)
            aggregate_ranking.sort(key=lambda x : x['avg_score'], reverse=True)

            # Topic-wise sorting is done after aggregate merging to preserve order until then
            for topic in topic_wise_ranking:
                topic_wise_ranking[topic].sort(key=lambda x : x['score'], reverse=True)
                # Keep only items that have a similarity score greater than 0.55
                topic_wise_ranking[topic] = filter(lambda x : x['score'] > 0.55, topic_wise_ranking[topic])
                print(topic + ' has ' + str(len(topic_wise_ranking[topic])) + ' entries')
        except Exception as e:
            print(e)


        # Find the largest, non-empty intersection of topics
        try:
            # Find the intersection of the most number of topics, and prioritize the combination with most rarity (within the given number of topics)
            common_items = []
            for size in range(len(topics), 0, -1):
                n_sized_combinations = map(list, list(itertools.combinations(topics, size)))
                print(n_sized_combinations)
                n_sized_combinations.sort(key=lambda comb : sum([x['rank'] for x in comb]))
                # Iterate in increasing order of frequency score
                for combination in n_sized_combinations:
                    print(combination)
                    combination_names = map(lambda x : x['topic'], combination)
                    common_items = find_topic_intersection(combination_names, topic_wise_ranking)
                    if common_items:
                        print(common_items)
                        print('arising out of')
                        print(combination_names)
                        break
                else:
                    # Nothing found
                    continue
                break
            else:
                print('No common ground found')
                # TODO Handle this case
            
            prettify_tag = lambda x : '"' + ' '.join(x.split('|')[0].split('_')) + '"'
            if common_items:
                combination = map(lambda x : x['topic'], combination)
                topics = map(lambda x : x['topic'], topics)
                present_tags = map(prettify_tag, combination)
                absent_tags = map(prettify_tag, list(set(topics) - set(combination)))
                dispatcher.utter_template('utter_compromise', present_tags=', '.join(present_tags), absent_tags=', '.join(absent_tags))
                dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(common_items[0]['eight_id']))

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
