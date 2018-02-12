import operator
import functools
import re

from nltk import pos_tag

# Custom stopwords list
stop = map(lambda x: x.strip(), open('code/data/words.txt', 'rb').readlines())


def prettify_topic(x):
    """Converts tokens in Sense2Vec compatible format to human readable format.

    For example, "machine_learning|NOUN" to "machine learning".
    """
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    """Converts a phrase (or word) to Sense2Vec compatible format noun.

    For example, "machine learning" to "machine_learning|NOUN". 
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return x.replace(' ', '_') + '|NOUN'


def split_tokens(x):
    """Splits token in Sense2Vec compatible format into individual words.

    For example, it splits "machine_learning|NOUN" into the list ["machine", "learning"].
    """
    return x.split('|')[0].split('_')


def merge_tokens(x):
    """Combines list of words into Sense2Vec compatible format noun.

    For example, it combines the list ["machine", "learning"] to "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return '_'.join(x) + '|NOUN'


def transform_doc_nltk(doc):
    doc = re.sub(r'[^\w\s]', '', doc).lower()
    tagged = pos_tag(doc.split())
    tags = ' '.join([x[1] for x in tagged])
    # Noun chaining with optional leading adjective
    matches = list(re.finditer('((JJ[A-Z]? )?)((NN[A-Z]? ?)+)', tags))
    noun_phrases = []
    for match in matches:
        chain_start_index = tags[:match.start() + 1].strip().count(' ')  # 4
        chain_end_index = tags[:match.end()].strip().count(' ')  #
        chain = tagged[chain_start_index: chain_end_index + 1]
        chain = '_'.join([x[0] for x in chain]) + '|NOUN'
        noun_phrases.append(chain)
    return ' '.join(noun_phrases)


def get_all_topics(message, transformed=False):
    message = message.encode('ascii', 'ignore')
    if not transformed:
        pos = transform_doc_nltk(message).split()
    else:
        pos = message.split()
    topics = filter(lambda x: x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x: x.split('|')[0] not in stop, topics)
    return topics
