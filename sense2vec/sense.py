import sense2vec

sense_vec_model = sense2vec.load()


def get_stop_words_list(path='code/words.txt'):
    """Read stopwords file and return it as a list."""
    stopwords = map(
        lambda x: x.strip(),
        open(path, 'rb').readlines()
    )
    return stopwords


stop_words = get_stop_words_list()
