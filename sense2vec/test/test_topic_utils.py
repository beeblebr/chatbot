import pytest

from ..sense import get_stop_words_list
from ..topic_utils import generate_variants


@pytest.fixture(scope='module')
def stop_words():
    return get_stop_words_list()


def test_generate_variants(stop_words):
    input_output_pairs = [
        (u'computer_engineering|NOUN', [
            'computer_engineering|NOUN'
        ]),
        (u'military_expenditure|NOUN', [
            'military_expenditure|NOUN'
        ]),
        (u'cost cutting measures|NOUN', [
            'cost_cutting|NOUN', 'measures|NOUN'
        ])
    ]
    for phrase, variants in input_output_pairs:
        assert set(generate_variants(phrase, stop_words)) == set(variants)
