from textpipe import pipeline


class Textpipe:

    def __init__(self):
        self.pipe = pipeline.Pipeline(['NWords', 'NSentences', 'Complexity'], language='nl')

    def analyze(self, text):
        analyzed = self.pipe(text)
        return analyzed['NWords'], analyzed['NSentences'], analyzed['Complexity']
