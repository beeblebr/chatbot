import re

from nltk import pos_tag

# Custom stopwords list
stop = map(lambda x: x.strip(), open('code/data/words.txt', 'rb').readlines())


def prettify_topic(x):
    """Convert tokens in Sense2Vec compatible format to human readable format.

    For example, "machine_learning|NOUN" to "machine learning".
    """
    return x.split('|')[0].replace('_', ' ')


def uglify_topic(x):
    """Convert a phrase (or word) to Sense2Vec compatible format noun.

    For example, "machine learning" to "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return x.replace(' ', '_') + '|NOUN'


def split_tokens(x):
    """Split token in Sense2Vec compatible format into individual words.

    For example, it splits "machine_learning|NOUN" into the list ["machine", "learning"].
    """
    return x.split('|')[0].split('_')


def merge_tokens(x):
    """Combine list of words into Sense2Vec compatible format noun.

    For example, it combines the list ["machine", "learning"] to "machine_learning|NOUN".
    NOTE: This method does not infer the POS tag. It always appends "|NOUN".
    """
    return '_'.join(x) + '|NOUN'


def transform_doc_nltk(doc):
    """Return transformed version of text where noun phrases are POS tagged in Sense2Vec compatible format.

    Args:
        doc: str
            Text to be transformed.

    Returns:
        str: The original text, with noun phrases tagged.
    """
    doc = re.sub(r'[^\w\s]', '', doc).lower()
    tagged = pos_tag(doc.split())
    tags = ' '.join([x[1] for x in tagged])
    # Noun chaining with optional leading adjective
    matches = list(re.finditer('((JJ[A-Z]? )?)((NN[A-Z]? ?)+)', tags))
    noun_phrases = []
    for match in matches:
        chain_start_index = tags[:match.start() + 1].strip().count(' ')
        chain_end_index = tags[:match.end()].strip().count(' ')
        chain = tagged[chain_start_index: chain_end_index + 1]
        chain = merge_tokens([x[0] for x in chain])
        noun_phrases.append(chain)
    return ' '.join(noun_phrases)


def get_all_topics(message, transformed=False):
    """Return list of potential topics from the given text.

    Topics are words / phrases extracted from the text according to the noun chaining algorithm in `transform_doc_nltk`. Stopwords are filtered out.

    Args:
        message: str
            User query.
        transformed: bool
            True if `message` is already POS-tagged, False otherwise.

    Returns:
        list: Potential topics.
    """
    message = message.encode('ascii', 'ignore')
    if not transformed:
        pos = transform_doc_nltk(message).split()
    else:
        pos = message.split()
    topics = filter(lambda x: x.split('|')[1] == 'NOUN', pos)
    topics = filter(lambda x: prettify_topic(x) not in stop, topics)    
    return topics
