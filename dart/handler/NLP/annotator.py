import spacy


class Annotator:

    nlp = spacy.load('nl_core_news_sm')

    def annotate(self, text):
        doc = self.nlp(text)
        entities = [{
            'text': e.text,
            'start_char': e.start_char,
            'end_char': e.end_char,
            'label': e.label_
        } for e in doc.ents]

        dependencies = [{
            'text': token.text,
            'dep': token.dep_,
            'head_text': token.head.text,
            'head_pos': token.head.pos_,
        } for token in doc]

        return doc, entities, dependencies

