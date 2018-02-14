import pytest

from .. import clarify
from ..sense import get_stop_words_list, sense_vec_model


@pytest.fixture(scope='function')
def stop_words():
    return get_stop_words_list()


def test_find_most_representative_topic(stop_words):
    candidate_topics = [
        u'machine_learning|NOUN',
        u'natural_language_processing|NOUN'
    ]
    representative_topic = clarify.find_most_representative_topic(candidate_topics)

    # Must not be None
    assert representative_topic

    # Must have rank greater than 1000
    assert sense_vec_model[unicode(representative_topic)][0] >= 1000

    # Must not be a stopword
    assert representative_topic not in stop_words
