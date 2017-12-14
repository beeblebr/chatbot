#!/usr/bin/env python -W ignore::DeprecationWarning
from nltk.stem import WordNetLemmatizer
from util.sense_utils import _transform_doc


lmt = WordNetLemmatizer()


def get_nltk_pos_tag(spacy_pos_tag):
	"""Convert Spacy style POS tags to NLTK style.
	Simply returns the first letter in lowercase"""
	return spacy_pos_tag[0].lower()


def lemmatize_sentence(sent):
	"""Lemmatizes each word of a sentence"""
	tagged = _transform_doc(sent, maintain_case=True).split()
	split_tagged = []
	for i in range(len(tagged)):
		word, spacy_pos = tagged[i].split('|')
		# If word is a noun phrase, distribute the POS tag to all the individual tags
		if '_' in word:
			split_tagged.extend(map(lambda x : x + '|' + spacy_pos, word.split('_')))
		else:
			split_tagged.append(word + '|' + spacy_pos)

	result = []
	# Perform word-level lemmatization and assemble reuslt
	for token in split_tagged:
		word, spacy_pos = token.split('|')
		try:
			result.append(lmt.lemmatize(word, get_nltk_pos_tag(spacy_pos)))
		except: # Invalid NLTK pos tag
			result.append(lmt.lemmatize(word))

	return ' '.join(result)
