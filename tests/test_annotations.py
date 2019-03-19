"""
Testing the outcome of annotations
"""

from dart.handler.NLP.annotator import Annotator

TEXT_1 = """"""

TEXT_2 = """Dit is een dummy"""

# https://www.nu.nl/economie/5798559/may-sluit-nieuwe-brexit-stemming-niet-uit-ondanks-oordeel-voorzitter.html
TEXT_3 = """De Britse overheid wil volgende week mogelijk alsnog voor een derde keer de Brexit-deal tot stemming laten brengen. Maandag oordeelde de voorzitter van het Britse Lagerhuis dat een nieuwe stemming alleen mag plaatsvinden als er iets wezenlijks verandert aan het voorstel.

Barclay suggereert dat de Britse regering "een manier" zal vinden om het voorstel toch in stemming te laten brengen. In de Britse politiek bepaalt de voorzitter van het parlement over welke voorstellen en moties wordt gestemd.
"""

annotator = Annotator()
doc1, ent1, tags1 = annotator.annotate(TEXT_1)
doc2, ent2, tags2 = annotator.annotate(TEXT_2)
doc3, ent3, tags3 = annotator.annotate(TEXT_3)


def test_entities():
    assert ent1 == []
    assert ent2 == []
    assert ent3 == [{'text': 'Britse', 'start_char': 3, 'end_char': 9, 'label': 'MISC'}, {'text': 'Brexit', 'start_char': 76, 'end_char': 82, 'label': 'PER'}, {'text': 'Britse', 'start_char': 156, 'end_char': 162, 'label': 'MISC'}, {'text': 'Lagerhuis', 'start_char': 163, 'end_char': 172, 'label': 'ORG'}, {'text': '\n\nBarclay', 'start_char': 271, 'end_char': 280, 'label': 'MISC'}, {'text': 'Britse', 'start_char': 299, 'end_char': 305, 'label': 'MISC'}, {'text': 'Britse', 'start_char': 396, 'end_char': 402, 'label': 'MISC'}]


def test_tags():
    assert tags1 == []
    assert tags2 == [{'text': 'Dit', 'tag': 'PRON'}, {'text': 'is', 'tag': 'VERB'}, {'text': 'een', 'tag': 'DET'}, {'text': 'dummy', 'tag': 'NOUN'}]
    assert tags3 == [{'text': 'De', 'tag': 'DET'}, {'text': 'Britse', 'tag': 'ADJ'}, {'text': 'overheid', 'tag': 'NOUN'}, {'text': 'wil', 'tag': 'VERB'}, {'text': 'volgende', 'tag': 'VERB'}, {'text': 'week', 'tag': 'NOUN'}, {'text': 'mogelijk', 'tag': 'ADJ'}, {'text': 'alsnog', 'tag': 'ADV'}, {'text': 'voor', 'tag': 'ADP'}, {'text': 'een', 'tag': 'DET'}, {'text': 'derde', 'tag': 'NUM'}, {'text': 'keer', 'tag': 'NOUN'}, {'text': 'de', 'tag': 'DET'}, {'text': 'Brexit', 'tag': 'NOUN'}, {'text': '-', 'tag': 'PUNCT'}, {'text': 'deal', 'tag': 'NOUN'}, {'text': 'tot', 'tag': 'ADP'}, {'text': 'stemming', 'tag': 'NOUN'}, {'text': 'laten', 'tag': 'VERB'}, {'text': 'brengen', 'tag': 'VERB'}, {'text': '.', 'tag': 'PUNCT'}, {'text': 'Maandag', 'tag': 'NOUN'}, {'text': 'oordeelde', 'tag': 'VERB'}, {'text': 'de', 'tag': 'DET'}, {'text': 'voorzitter', 'tag': 'NOUN'}, {'text': 'van', 'tag': 'ADP'}, {'text': 'het', 'tag': 'DET'}, {'text': 'Britse', 'tag': 'ADJ'}, {'text': 'Lagerhuis', 'tag': 'NOUN'}, {'text': 'dat', 'tag': 'CONJ'}, {'text': 'een', 'tag': 'DET'}, {'text': 'nieuwe', 'tag': 'ADJ'}, {'text': 'stemming', 'tag': 'NOUN'}, {'text': 'alleen', 'tag': 'ADV'}, {'text': 'mag', 'tag': 'VERB'}, {'text': 'plaatsvinden', 'tag': 'VERB'}, {'text': 'als', 'tag': 'CONJ'}, {'text': 'er', 'tag': 'ADV'}, {'text': 'iets', 'tag': 'PRON'}, {'text': 'wezenlijks', 'tag': 'ADJ'}, {'text': 'verandert', 'tag': 'VERB'}, {'text': 'aan', 'tag': 'ADP'}, {'text': 'het', 'tag': 'DET'}, {'text': 'voorstel', 'tag': 'NOUN'}, {'text': '.', 'tag': 'PUNCT'}, {'text': '\n\n', 'tag': 'SPACE'}, {'text': 'Barclay', 'tag': 'NOUN'}, {'text': 'suggereert', 'tag': 'VERB'}, {'text': 'dat', 'tag': 'CONJ'}, {'text': 'de', 'tag': 'DET'}, {'text': 'Britse', 'tag': 'ADJ'}, {'text': 'regering', 'tag': 'NOUN'}, {'text': '"', 'tag': 'PUNCT'}, {'text': 'een', 'tag': 'DET'}, {'text': 'manier', 'tag': 'NOUN'}, {'text': '"', 'tag': 'PUNCT'}, {'text': 'zal', 'tag': 'VERB'}, {'text': 'vinden', 'tag': 'VERB'}, {'text': 'om', 'tag': 'CONJ'}, {'text': 'het', 'tag': 'DET'}, {'text': 'voorstel', 'tag': 'NOUN'}, {'text': 'toch', 'tag': 'ADV'}, {'text': 'in', 'tag': 'ADP'}, {'text': 'stemming', 'tag': 'NOUN'}, {'text': 'te', 'tag': 'ADP'}, {'text': 'laten', 'tag': 'VERB'}, {'text': 'brengen', 'tag': 'VERB'}, {'text': '.', 'tag': 'PUNCT'}, {'text': 'In', 'tag': 'ADP'}, {'text': 'de', 'tag': 'DET'}, {'text': 'Britse', 'tag': 'ADJ'}, {'text': 'politiek', 'tag': 'NOUN'}, {'text': 'bepaalt', 'tag': 'VERB'}, {'text': 'de', 'tag': 'DET'}, {'text': 'voorzitter', 'tag': 'NOUN'}, {'text': 'van', 'tag': 'ADP'}, {'text': 'het', 'tag': 'DET'}, {'text': 'parlement', 'tag': 'NOUN'}, {'text': 'over', 'tag': 'ADP'}, {'text': 'welke', 'tag': 'PRON'}, {'text': 'voorstellen', 'tag': 'NOUN'}, {'text': 'en', 'tag': 'CONJ'}, {'text': 'moties', 'tag': 'NOUN'}, {'text': 'wordt', 'tag': 'VERB'}, {'text': 'gestemd', 'tag': 'VERB'}, {'text': '.', 'tag': 'PUNCT'}, {'text': '\n', 'tag': 'SPACE'}]
