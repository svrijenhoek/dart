import csv
import os
import spacy
from collections import defaultdict
import re


"""
File to determine the confidence of found cues. If this cue is found in a sentence, how likely is it to be an 
actual indication of an opinion?
"""

# file location of the found cues for each dataset
file_ajax = 'C:\\Users\\Sanne\\Documents\\Maaike\\cues_ajax.csv'
file_steur = 'C:\\Users\\Sanne\\Documents\\Maaike\\cues_steur.csv'
# load spacy model, disable named entity recognition and POS tagging (we only need to separate sentences)
nlp = spacy.load('nl_core_news_sm', disable=['tagger, ner'])
# change csv delimiter
csv.register_dialect('colon', delimiter=';')


def get_cues():
    cues = {}
    # open the CSV files with all cues and their frequencies
    for file in [file_ajax, file_steur]:
        with open(file, 'r') as csvFile:
            reader = csv.reader(csvFile, dialect='colon')
            for row in reader:
                cue = row[0]
                cue = cue.replace('...', '(.*)')
                frequency = int(row[1])
                if cue in cues:
                    cues[cue] = cues[cue] + frequency
                else:
                    cues[cue] = frequency
        csvFile.close()
    return cues


def get_files():
    # generate a file list of all text files
    folder_steur = "C:\\Users\\Sanne\\PycharmProjects\\DART\\output\\steur"
    folder_ajax = "C:\\Users\\Sanne\\PycharmProjects\\DART\\output\\ajax"

    files = []
    for folder in [folder_steur, folder_ajax]:
        for r, d, f in os.walk(folder):
            for file in f:
                if '.txt' in file:
                    files.append(os.path.join(r, file))
    return files


def get_all_cue_occurrences(cues, files):
    # iterate over all documents, and see how often they appear in total (not necessarily as cue)
    cue_presence = defaultdict(int)
    for file in files:
        with open(file, "r+") as data:
            text = data.read()
            document = nlp(text)
            sentences = [sent.string.strip() for sent in document.sents]
            for sentence in sentences:
                for cue in cues:
                    if cue == ":":
                        full = cue
                    else:
                        full = " "+cue.strip()+" "
                    if "(.*)" in full:
                        x = re.search(full, sentence)
                        if x:
                            cue_presence[cue] += 1
                    else:
                        if full in sentence:
                            cue_presence[cue] += 1
    return cue_presence


def get_confidence(cues, cue_presence):
    # calculate the ratio of 'cue found as regular text'to 'cue found as actual cue'
    # sometimes a cue is more often found through annotation than it was by the computers.
    # This happens for example when an annotation spans multiple sentences. We still need to figure out a way to
    # deal with that
    cue_confidence = {}
    problematic = []
    for cue in cues:
        try:
            confidence = cues[cue] / cue_presence[cue]
            cue_confidence[cue] = confidence
            if confidence > 1:
                problematic.append(cue)
        except ZeroDivisionError:
            problematic.append(cue)
    # for item in cue_confidence:
        # print("{}\t{}".format(item, cue_confidence[item]))
    return cue_confidence, problematic


def analyze_problems(problematic, files):
    # for analysis purposes
    # for all problematic cues that were found (annotated/all > 1) print the sentences where the cue was matched
    problematic_sentences = []
    for file in files:
        with open(file, "r+") as data:
            content = data.read()
            doc = nlp(content)
            sentences = [sent.string.strip() for sent in doc.sents]
            for sentence in sentences:
                for cue in problematic:
                    if cue == ":":
                        full = cue
                    else:
                        full = " "+cue.strip()+" "
                    if "(.*)" in full:
                        x = re.search(full, sentence)
                        if x:
                            problematic_sentences.append(cue + "\t" + sentence)
                    else:
                        if full in sentence:
                            problematic_sentences.append(cue + "\t" + sentence)
    for sentence in problematic_sentences:
        print(sentence)


def main():
    cues = get_cues()
    files = get_files()
    occurrences = get_all_cue_occurrences(cues, files)
    confidence, problems = get_confidence(cues, occurrences)
    print(confidence)
    analyze_problems(problems, files)


if __name__ == "__main__":
    main()
