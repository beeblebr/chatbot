from util.topic_utils import get_top_categories, clean_text
from util.sense_utils import transform_topics, sense_topic_similarity, _transform_doc

def get_all_topics(message):
    # Extract entities from message
    message_text = message.text
    entities = message.entities

    nlu_topics = map(lambda x : x['value'], filter(lambda x : x['entity'] == 'topic', entities))
    pos = _transform_doc(message_text).split()
    pos = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    pos = map(lambda x : x.split('|')[0].replace('_', ' '), pos)
    nlu_topics.extend(pos)
    nlu_topics = list(set(nlu_topics))  
    query = filter(lambda x : x['entity'] == 'query', entities)

    # Word2Vec fallback topic extraction
    fallback_topics = get_top_categories(clean_text(message_text))

    return {'nlu_topics': nlu_topics, 'fallback_topics': fallback_topics}

# Remove this later
def get_all_topics_plain(message_text):
    pos = _transform_doc(message_text).split()
    pos = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    pos = map(lambda x : x.split('|')[0].replace('_', ' '), pos)
    nlu_topics = pos    

    fallback_topics = get_top_categories(clean_text(message_text))
    return {'nlu_topics': nlu_topics, 'fallback_topics': fallback_topics}