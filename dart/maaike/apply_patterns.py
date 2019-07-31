import os
import spacy
import regex as re
import csv

"""
File that applies a constructed pattern for opinion holding on a specified corpus of texts
"""

# location of text files
folder = "C:\\Users\\m2a_h\\Documents\\VU\\Research Master Linguistics\\SCRIPTIE\\Corpus\\Weinstein\\"
pattern_file = "C:\\Users\\m2a_h\\Documents\\VU\\Research Master Linguistics\\SCRIPTIE\\Patronen\\patterns.txt"
# spacy model for NLP
nlp = spacy.load('nl_core_news_sm')


def generalize_pattern(p):
    # prepare pattern for regular expressions
    pattern_generic = p.replace("<SOURCE>", "(.*)").replace("<CONTENT>", "(.*)").rstrip()
    # see if in the original pattern the source was mentioned first or the content
    if p.find('<CONTENT>') < p.find('<SOURCE>'):
        content_location = 1
        source_location = 2
    else:
        source_location = 1
        content_location = 2
    return pattern_generic, source_location, content_location


def filter_source(raw, s, position):
    """
    method that takes a raw source (everything matched by the regular expression and aims to reduce it to only the
    relevant part
    """
    # first see if we can find named entities of type PERSON
    candidates = [ent.text for ent in s.ents if ent.label_ == 'PER' and ent.text in raw]
    # if not, find pronouns
    if len(candidates) == 0:
        candidates = [token.text for token in s if token.pos_ == 'PRON' and token.text in raw]
    # if not, find proper nouns
    if len(candidates) == 0:
        candidates = [token.text for token in s if token.pos_ == 'PROPN' and token.text in raw]
    # if not, find regular nouns
    if len(candidates) == 0:
        candidates = [token.text for token in s if token.pos_ == 'NOUN' and token.text in raw]

    # what to do if we find multiple or none candidates
    if len(candidates) == 1:
        return candidates[0]
    elif len(candidates) > 1:
        if position == 1:
            return candidates[0]
        else:
            return candidates[0]
    # if all else fails, just leave the source as it was
    return raw


def match_patterns(file, patterns):
    # open the file, enrich the information, and attempt to match the specified pattern to each sentence
    with open(file) as data:
        text = data.read()
        text = text.replace('|', ' ')
        doc = nlp(text)
        for sentence in doc.sents:
            first_match = True
            for p in patterns:
                if not p == "\n":
                    pattern, source_location, content_location = generalize_pattern(p)
                    x = re.search(pattern, sentence.text)
                    if x:
                        if first_match:
                            print("SENTENCE: "+sentence.text)
                            first_match = False
                        content = x.group(content_location)
                        source = x.group(source_location)
                        source = filter_source(source, sentence, source_location)
                        print("\t"+pattern+"\t"+source+"\t"+content+"\t"+sentence.text)




def read_pattern_file(location):
    f = open(location, "r")
    data = f.readlines()
    return data


def main():
    # get list of all files in specified folder
    files = []
    for r, d, f in os.walk(folder):
        for file in f:
            if '.txt' in file:
                files.append(os.path.join(r, file))

    patterns = read_pattern_file(pattern_file)
    for file in files:
        match_patterns(file, patterns)


if __name__ == "__main__":
    main()
