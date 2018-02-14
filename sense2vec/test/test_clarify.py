import pytest

from code.clarify import find_most_representative_topic


def test_find_most_representative_topic():
    candidate_topics = [
        'machine_learning|NOUN', 'natural_language_processing|NOUN'
    ]

    representative_topic = find_most_representative_topic(candidate_topics)

    assert len(representative_topic) == 1
