from nltk.corpus import stopwords

from util.topic_utils import get_top_categories
from util.sense_utils import transform_topics, _transform_doc


stop = map(unicode, set(stopwords.words('english')))

def get_all_topics(message):
    # Extract entities from message
    message_text = message.text
    entities = message.entities

    # nlu_topics = _transform_doc(message_text).split()
    pos = _transform_doc(message_text).split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)

    # Word2Vec fallback topic extraction
    fallback_topics = get_top_categories(message_text)

    return {'nlu_topics': nlu_topics, 'fallback_topics': fallback_topics}


# Remove this later
def get_all_topics_plain(message_text):
    message_text = message_text.encode('ascii', 'ignore')
    pos = _transform_doc(message_text).split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)

    # Word2Vec fallback topic extraction
    #fallback_topics = get_top_categories(message_text)

    return {'nlu_topics': nlu_topics}


def get_topics_from_transformed_text(transformed_text):
    pos = transformed_text.split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)
    return {'nlu_topics': nlu_topics}