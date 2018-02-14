import pytest

from clarify import find_most_representative_topic
from sense import get_stop_words_list


@pytest.fixture(scope='module')
def stop_words():
    return get_stop_words_list('words.txt')


def test_find_most_representative_topic(stop_words):
    candidate_topics = [
        'machine_learning|NOUN', 'natural_language_processing|NOUN'
    ]
    representative_topic = find_most_representative_topic(candidate_topics)
    assert len(representative_topic) == 1
