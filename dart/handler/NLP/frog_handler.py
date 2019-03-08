import requests
import xml.etree.ElementTree as ElementTree
import dart.Util


class FrogHandler:

    def __init__(self, name):
        self.url = 'http://192.168.99.100:8080/frog/'+name

    def create_project(self):
        requests.put(self.url)

    def delete_project(self):
        requests.delete(self.url)

    def add_document(self, content, filename=dart.Util.random_string(6)):
        params = {'inputtemplate': 'maininput', 'contents': content}
        requests.post(self.url + '/input/'+filename, params=params)

    # The chunker is skipped as it causes an internal error in frog
    def start_execution(self):
        params = {'skip': ['m', 'p', 'c']}
        requests.post(self.url, params=params)

    def processing_finished(self):
        r = requests.get(self.url)
        root = ElementTree.fromstring(r.content)
        status = root.findall('.//status')[0].get('code')
        return status == '2'

    def get_filelist(self):
        r = requests.get(self.url)
        root = ElementTree.fromstring(r.content)
        files = [child.text for child in root.findall('.//output//file//name') if child.text.endswith('.xml')]
        return files

    def download_files(self, files):
        for file in files:
            try:
                r = requests.get(self.url + '/output/' + file)
                f = open('../../output/frog/'+file, "a")
                f.write(r.text)
            except UnicodeEncodeError:
                print("Encoding error")
