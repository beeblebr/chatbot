import pickle
import re

from nltk.corpus import stopwords

from util.topic_utils import get_top_categories
from util.sense_utils import _transform_doc, _transform_doc_nltk

stop = map(unicode, set(stopwords.words('english')))
dictionary = map(lambda x : x.strip(), open('words.txt', 'rb').readlines())
alpha = map(lambda x : x.strip(), open('words_alpha.txt', 'rb').readlines())
dictionary = set(dictionary).union(set(alpha))
# dictionary = pickle.load(open('keys', 'rb'))

def get_all_topics(message):
    # Extract entities from message
    message_text = message.text
    entities = message.entities

    # nlu_topics = _transform_doc(message_text).split()
    # pos = _transform_doc(message_text).split()
    pos = _transform_doc_nltk(message_text).split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)

    # Word2Vec fallback topic extraction
    fallback_topics = get_top_categories(message_text)

    return {'nlu_topics': nlu_topics, 'fallback_topics': fallback_topics}


def get_all_topics_plain(message_text):
    message_text = message_text.encode('ascii', 'ignore')
    pos = _transform_doc_nltk(message_text).split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)

    return {'nlu_topics': nlu_topics}


def get_topics_from_transformed_text(transformed_text):
    pos = transformed_text.split()
    nlu_topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    nlu_topics = filter(lambda x : x.split('|')[0] not in stop, nlu_topics)
    return {'nlu_topics': nlu_topics}


# def get_miscapitalized_words(text):
#     """Returns capitalized words that are not proper nouns with their lowercase forms"""
#     conflicts = []
#     # Remove punctuation
#     text = re.sub(r'[^\w\s]', '', text)
#     # Ignore first word
#     for word in text.split()[1:]:
#         if not word.islower() and word.lower() in dictionary:
#             # Only lowercase is in dictionary
#             conflicts.append(word)
#     return conflicts


# def resolve_miscapitalization_conflicts(text, accidentally_capitalized):
#     result = []
#     for word in text.split():
#         word = re.sub(r'[^\w\s]', '', word)
#         if word in accidentally_capitalized:
#             result.append(word.lower())
#         else:
#             result.append(word)
#     return ' '.join(result)
