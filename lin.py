from nltk import word_tokenize, pos_tag
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from nltk.corpus import wordnet_ic
ic = wordnet_ic.ic('ic-brown.dat')
 
def penn_to_wn(tag):
    if tag.startswith('N'):
        return 'n'
 
    if tag.startswith('V'):
        return 'v'
 
    if tag.startswith('J'):
        return 'a'
 
    if tag.startswith('R'):
        return 'r'
 
    return None
 
def tagged_to_synset(word, tag):
    wn_tag = penn_to_wn(tag)
    if wn_tag is None:
        return None
 
    try:
        return wn.synsets(word, wn_tag)[0]
    except:
        return None
 
def sentence_similarity(sentence1, sentence2):
    """ compute the sentence similarity using Wordnet """
    # Tokenize and tag
    sentence1 = pos_tag(word_tokenize(sentence1))
    sentence2 = pos_tag(word_tokenize(sentence2))
 
    # Get the synsets for the tagged words
    synsets1 = [tagged_to_synset(*tagged_word) for tagged_word in sentence1]
    synsets2 = [tagged_to_synset(*tagged_word) for tagged_word in sentence2]
 
    # Filter out the Nones
    synsets1 = [ss for ss in synsets1 if ss]
    synsets2 = [ss for ss in synsets2 if ss]
 
    score, count = 0.0, 0
 
    # For each word in the first sentence
    for synset in synsets1:
        # Get the similarity value of the most similar word in the other sentence
    	best_score = 0
    	for ss in synsets2:
    	    try:
                best_score2 = synset.lin_similarity(ss,ic)
    	        if best_score2 > best_score:
    		    best_score = best_score2
    	    except:
    		  pass
     
     
        # Check that the similarity could have been computed
        if best_score is not None:
            score += best_score
            count += 1
 
    # Average the values
    score /= max(1, count)
    return score
 
 
def similarity(params):
    sentence1, sentence2, i = params
    """ compute the symmetric sentence similarity using Wordnet """
    return ((sentence_similarity(sentence1, sentence2) + sentence_similarity(sentence2, sentence1)) / 2.0, i)

def similarity_score(a, b):
    return (sentence_similarity(a, b) + sentence_similarity(b, a)) / 2.0

if __name__ == '__main__':
    from generator import evaluate

    evaluate(similarity)
