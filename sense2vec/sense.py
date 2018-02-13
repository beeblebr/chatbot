import sense2vec

sense_vec_model = sense2vec.load()
stop = map(lambda x: x.strip(), open('code/words.txt', 'rb').readlines())
