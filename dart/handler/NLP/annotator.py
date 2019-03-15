import spacy


class Annotator:

    nlp = spacy.load('nl_core_news_sm', disable=['parser'])

    def annotate(self, text):
        doc = self.nlp(text)
        entities = [{
            'text': e.text,
            'start_char': e.start_char,
            'end_char': e.end_char,
            'label': e.label_
        } for e in doc.ents]

        tags = [{
            'text': token.text,
            'tag': token.pos_
        } for token in doc]

        return doc, entities, tags

