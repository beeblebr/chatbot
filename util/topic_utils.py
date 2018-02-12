import operator
import functools
import re

from nltk import pos_tag

# Custom stopwords list
stop = map(lambda x : x.strip(), open('code/data/words.txt', 'rb').readlines())


def transform_doc_nltk(doc, maintain_case=False):  
    doc = re.sub(r'[^\w\s]', '', doc).lower()
    tagged = pos_tag(doc.split())
    tags = ' '.join([x[1] for x in tagged])
    # Noun chaining with optional leading adjective
    matches = list(re.finditer('((JJ[A-Z]? )?)((NN[A-Z]? ?)+)', tags))
    noun_phrases = []
    for match in matches:
        chain_start_index = tags[:match.start() + 1].strip().count(' ')  # 4
        chain_end_index = tags[:match.end()].strip().count(' ')  #  
        chain = tagged[chain_start_index : chain_end_index + 1]
        chain = '_'.join([x[0] for x in chain]) + '|NOUN'
        noun_phrases.append(chain)
    return ' '.join(noun_phrases)


def prettify_topic(x):
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    return x.replace(' ', '_') + '|NOUN'


def get_all_topics(message, transformed=False):
    message = message.encode('ascii', 'ignore')
    if not transformed:
        pos = transform_doc_nltk(message).split()
    else:
        pos = message.split()
    topics = filter(lambda x : x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x : x.split('|')[0] not in stop, topics)
    return topics
