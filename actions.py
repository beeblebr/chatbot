from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet

from rasa_config import *

from util.sense_utils import transform_topics, sense_topic_similarity, _transform_doc
from util.chat_utils import get_all_topics
from util.topic_utils import get_top_categories, clean_text

from util.db_utils import *



class ActionSearchKnowledgeBase(Action):

    def name(self):
        return 'action_search_knowledge_base'


    def run(self, dispatcher, tracker, domain):
        print('calllllllllllllllllllllllllled')
        message = tracker.latest_message

        all_topics = get_all_topics(message)

        if 'nlu_topics' not in all_topics:
            nlu_topics = all_topics.get('fallback_topics', [])
        else:
            nlu_topics = all_topics.get('nlu_topics', [])

        ranked = []
        count = 1
        print('im here')
        for k in get_knowledge_corpus():
            print(count)
            count += 1
            k_nlu_topics = k.get('nlu_topics', [])
            print(k_nlu_topics)
            k_fallback_topics = k.get('fallback_topics', [])

            if not k_nlu_topics:
                k_nlu_topics = k_fallback_topics = k.get('top_cats')

            print('getting similarity score')
            similarity_score = sense_topic_similarity(transform_topics(k_nlu_topics), transform_topics(nlu_topics))

            print(similarity_score)

            ranked.append((similarity_score, k))

        ranked.sort(reverse=True)

        print(ranked[0][1]['text'])

        return [SlotSet("eight_id", ranked[0][1]['eight_id'])]


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


