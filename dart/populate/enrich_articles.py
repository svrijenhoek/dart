import pandas as pd

import dart.handler.NLP.annotator
import dart.handler.NLP.textpipe_handler
import dart.handler.NLP.enrich_entities
import dart.handler.other.openstreetmap
import dart.handler.other.wikidata
import dart.handler.NLP.classify_on_entities
import dart.Util

import sys


class Enricher:

    def __init__(self, handlers, metrics):
        self.handlers = handlers
        self.metrics = metrics
        self.annotator = dart.handler.NLP.annotator.Annotator()
        self.textpipe = dart.handler.NLP.textpipe_handler.Textpipe()
        self.spacy_tags = ['DET', 'ADP', 'PRON']
        self.enricher = dart.handler.NLP.enrich_entities.EntityEnricher(self.metrics)
        self.classifier = dart.handler.NLP.classify_on_entities.Classifier()

    def annotate_entities(self, entities):
        annotated_entities = []
        for entity in (entity for entity in entities if 'annotated' not in entity or entity['annotated'] == 'N'):
            entity = self.enricher.enrich(entity)
            annotated_entities.append(entity)
        return annotated_entities

    def calculate_tags(self, tags):
        """
        calculates for each tag specified its representation in the selected article
        """
        df = pd.DataFrame.from_dict(tags)
        counts = df.tag.value_counts()
        result = {}
        for tag in self.spacy_tags:
            try:
                count = counts[tag]
                percentage = count / len(df)
                result[tag] = percentage
            except KeyError:
                result[tag] = 0
        return result

    def enrich_all(self):
        try:
            recommendations = self.handlers.recommendations.get_all_recommendations()
            for recommendation in recommendations:
                article = self.handlers.articles.get_by_id(recommendation.article_id)
                if not article.annotated == 'Y':
                    doc = {'id': article.id}
                    if not article.entities:
                        _, entities, tags = self.annotator.annotate(article.text)
                    else:
                        entities = article.entities
                        tags = article.tags
                    enriched_entities = self.annotate_entities(entities)
                    doc['entities'] = enriched_entities
                    doc['tags'] = tags

                    if 'length' or 'complexity' in self.metrics:
                        if not article.nsentences or not article.nwords or not article.complexity:
                            # rewrite
                            nwords, nsentences, complexity = self.textpipe.analyze(article.text)
                            doc['nwords'] = nwords
                            doc['nsentences'] = nsentences
                            doc['complexity'] = complexity
                    if 'emotive' in self.metrics and not article.tag_percentages:
                        percentages = self.calculate_tags(tags)
                        doc['tag_percentages'] = percentages
                    if 'classify' in self.metrics:
                        if 'entities' not in doc:
                            classification = 'Onbekend'
                        else:
                            classification, scope = self.classifier.classify(doc['entities'])
                        doc['classification'] = classification
                        doc['scope'] = scope
                    doc['annotated'] = 'Y'
                    self.handlers.articles.update_doc(article.id, doc)
                    self.handlers.recommendations.update_doc(article.id, doc)
            self.enricher.save()
        except ConnectionError:
            self.enricher.save()
            print("Connection error!")
            sys.exit()
        self.enricher.save()



