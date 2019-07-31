import xml.etree.ElementTree as ET
import spacy
import re
import os

base = "C:\\Users\\Sanne\\Google Drive\\Maaike - scriptie\\"
ajax_corpus = base+"Corpus\\Ajax\\"
steur_corpus = base+"Corpus\\vdSteur\\"

nlp = spacy.load('nl_core_news_sm')


def enrich_text(file_loc):
    # apply spaCy NER, POS tagging and dependency parsing
    # note: spaCy's Dutch language model does not have noun chunks!
    with open(file_loc) as data:
        text = data.read()
    # remove all (probably faulty) '|'s
    text = text.replace("|", ". ")
    doc = nlp(text)
    return doc


def analyze_annotation(annotation, file_loc):
    try:
        doc = enrich_text(file_loc)
        cue = annotation[0]
        source = annotation[1]
        content = annotation[2]
        for sent in doc.sents:
            sentence = sent.text
            if "..." in cue:
                cue = cue.replace("...", "(.*)")
                # check if the pattern matches the sentence
                x = re.search(cue, sentence)
                # if there is a match
                if x and source in sentence and content in sentence:
                    # replace with placeholders
                    sentence = sentence.replace(source, "<SOURCE>")
                    sentence = sentence.replace(content, "<CONTENT>")
                    # save the pattern
                    print(cue + "\t" + source + "\t" + content + "\t" + sentence)
            else:
                # if cue, content and source are in the sentence
                if cue in sentence and source in sentence and content in sentence:
                    # replace with placeholders
                    sentence = sentence.replace(source, "<SOURCE>")
                    sentence = sentence.replace(content, "<CONTENT>")
                    # save the pattern
                    print(cue + "\t" + source + "\t" + content + "\t" + sentence)
    # mysterious error I don't quite understand
    except TypeError:
        pass


def read_xml(xml_file):
    output = []
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # find all cues
    for node in root.findall("classMention/mentionClass[@id='CUE']/..."):
        cue = node.find("mentionClass[@id='CUE']").text
        source = ''
        content = ''
        # retrieve the links to the source and content
        links = [child.attrib['id'] for child in node]
        links.remove('CUE')
        # follow the links and retrieve the appropriate text
        for link in links:
            link_node = root.find("complexSlotMention[@id='"+link+"']")
            link_id = link_node[1].attrib['value']
            final = root.find("classMention[@id='" + link_id + "']/mentionClass")
            if final.attrib['id'] == 'SOURCE':
                source = final.text
            elif final.attrib['id'] == 'CONTENT':
                content = final.text
        output.append([cue, source, content])
    return output


def main():
    # start of program
    # retrieve all texts
    files = []
    for folder in [ajax_corpus, steur_corpus]:
        for r, d, f in os.walk(folder):
            for file in f:
                if '.txt' in file:
                    files.append(os.path.join(r, file))

    # for all annotated files, generate patterns
    for file in files:
        xml_location = file.replace("Corpus", "Geannoteerd")+'.knowtator.xml'
        annotations = read_xml(xml_location)
        for a in annotations:
            analyze_annotation(a, file)


if __name__ == "__main__":
    main()
