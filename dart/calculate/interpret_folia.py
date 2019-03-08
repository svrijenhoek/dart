import xml.etree.ElementTree as ET

tree = ET.parse('../../output/frog/BASFT1.xml')
root = tree.getroot()

words = [child.text for child in root.findall('.//{http://ilk.uvt.nl/folia}w/{http://ilk.uvt.nl/folia}t')]
print(' '.join(words))
lemmas = [child.get('class') for child in root.findall('.//{http://ilk.uvt.nl/folia}lemma')]
print(' '.join(lemmas))

entities = []
