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

from util.sense_utils import perform_batch_call
from util.chat_utils import get_all_topics
from util.topic_utils import assemble_topic_wise_rankings, get_aggregate_scores, find_topic_intersection, hashabledict
from util.db_utils import *


class ActionSearchKnowledgeBase(Action):
    """Handles intent to query knowledge base"""

    def name(self):
        return 'action_search_knowledge_base'


    def run(self, dispatcher, tracker, domain):
        user_id = tracker.slots['user_id'].value
        message = tracker.latest_message.text

        add_question_to_user_history(user_id, message)
        # Get topics (noun phrases) for both query and every knowledge item
        try:
            query_topics = {'text': get_all_topics(message)}
            print(query_topics)
            corpus = list(get_knowledge_corpus(exclude_user=user_id))
            corpus_topics_map = [{'text': get_all_topics(item['transformed_text'], transformed=True)} for item in corpus]
            # Perform network request
            similarity_map = perform_batch_call({'query_topics': query_topics, 'corpus_topics_map': corpus_topics_map})
        except Exception as e:
            print(e)
        
        # Get topic wise ranking
        topic_wise_ranking = assemble_topic_wise_rankings(
            similarity_map, corpus)
        # Calculate average similarity scores over all topic perspectives
        aggregate_ranking = get_aggregate_scores(
            topic_wise_ranking, corpus)
        aggregate_ranking.sort(key=lambda x: x['avg_score'], reverse=True)


        # Topic-wise sorting was deferred until aggregate merging to
        # preserve order
        for topic in topic_wise_ranking:
            topic_wise_ranking[topic].sort(
                key=lambda x: x['score'], reverse=True)
            # Keep only items that have a similarity score greater than 60%
            topic_wise_ranking[topic] = filter(
                lambda x: x['score'] > 0.6, topic_wise_ranking[topic])
            print(topic + ' has ' +
                  str(len(topic_wise_ranking[topic])) + ' entries')
        

        # Get the list of topics along with their ranks (from the server
        # response)
        topics = [topic.copy() for topic in similarity_map[0]]

        # Find the intersection of the most number of topics, and
        # prioritize the combination with most rarity (within the given
        # number of topics)
        common_items = []
        for size in range(len(topics), 0, -1):
            # Get all combinations of topics of length `size`
            n_sized_combinations = map(list, list(
                itertools.combinations(topics, size)))
            # The metric for rarity is the sum of Sense2Vec ranks of all
            # topics in the combination
            n_sized_combinations.sort(
                key=lambda comb: sum([x['rank1'] for x in comb]))

            # Iterate in decreasing order of rarity
            for combination in n_sized_combinations:
                combination_names = map(lambda x: x['topic'], combination)
                common_items = find_topic_intersection(
                    combination_names, topic_wise_ranking)
                common_items.sort(key=lambda x: x['score'], reverse=True)
                if common_items:
                    print('{0} common items'.format(len(common_items)))
                    print('\n')
                    break
            else:
                # Reduce combination size by 1 and continue
                continue
            if common_items:
                break
        else:
            print('Nothing found')
            dispatcher.utter_template('utter_nothing_found')
            response = {'type': 'nothing_found'}
            return [SlotSet('response_metadata', response)]


        prettify_variant = lambda x: ' '.join(x['matched_variant'].split('|')[0].split('_'))
        # matched_variants = list(set(map(prettify_variant, common_items)))
        matched_variants = list(set(sorted(common_items, key=lambda x : x['rank2'], reverse=True)))
        print(map(lambda x : (x['matched_variant'], x['rank2']), matched_variants))
        # from sklearn.cluster import KMeans
        # y_pred = KMeans(n_clusters=min(len(matched_variants), 6), random_state=170).fit_predict(X)



        prettify_tag = lambda x: '"' + \
            ' '.join(x.split('|')[0].split('_')) + '"'

        # Extract topic names from the dicts containing ranks
        combination = map(lambda x: x['topic'], combination)
        topics = map(lambda x: x['topic'], topics)

        present_tags = map(prettify_tag, combination)
        absent_tags = map(prettify_tag, list(
            set(topics) - set(combination)))

        if not absent_tags:
            dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(
                common_items[0]['eight_id']))
            response = {'type': 'found', 'top_matches': common_items}
        else:
            dispatcher.utter_template('utter_compromise', present_tags=', '.join(
                present_tags), absent_tags=', '.join(absent_tags))
            dispatcher.utter_template('utter_can_help_you_with_that', name=get_name_from_id(
                common_items[0]['eight_id']))
            response = {'type': 'compromise',
                        'top_matches': common_items}
        return [SlotSet('response_metadata', response)]


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
