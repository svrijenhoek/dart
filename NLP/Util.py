import spacy
from spacy.tokens import Doc


nlp = spacy.load('nl_core_news_sm')


def to_bytes(doc):
    return doc.to_bytes()


def from_bytes(bytes_obj):
    doc = Doc(nlp.vocab).from_bytes(bytes_obj)
    return doc
