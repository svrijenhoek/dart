from textpipe import pipeline


class Textpipe:

    def __init__(self, lang):
        if lang == 'dutch':
            language = 'nl'
        elif lang == 'english':
            language = 'en'
        elif lang == 'german':
            language = 'de'

        self.pipe = pipeline.Pipeline(['NWords', 'NSentences', 'Complexity'], language=language)

    def analyze(self, text):
        analyzed = self.pipe(text)
        return analyzed['NWords'], analyzed['NSentences'], analyzed['Complexity']
