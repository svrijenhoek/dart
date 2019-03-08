import csv
from datetime import datetime as dt
from dart.handler.elastic.article_handler import ArticleHandler
from dart.models.Article import Article


searcher = ArticleHandler()


def make_txt(title, date, author, source, text):
    body = "{}\n{}, {}, {}\n\n{}".format(title, date, author, source, text)
    filename = source + '_' + date
    filename = filename.replace(":", "-")
    try:
        with open("C:\\Users\\Sanne\\PycharmProjects\\DART\\output\\van der Steur\\"+source+"\\"+filename+".txt", "w") as text_file:
            text_file.write(body)
    except UnicodeEncodeError:
        pass


source = "C:\\Users\\Sanne\\PycharmProjects\\DART\\data\\input.csv"
with open(source, 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        id = row[0]
        document = Article(searcher.get_by_id('articles', id))
        date = document.publication_date
        title = document.title
        text = document.text
        try:
            author = document.author
        except KeyError:
            author = ''
        source = document.doctype
        make_txt(title, date, author, source, text)

# # iterate over all the files in the data folder
# for path, subdirs, files in os.walk():
#     for name in files:
#         print(name)
#         # assumes all files are json-l, change this to something more robust!
#         for line in open((os.path.join(path, name))):
#             try:
#                 json_doc = json.loads(line)
#                 date = json_doc['publication_date']
#                 date_str = dt.strptime(date, "%Y-%m-%dT%H:%M:%S")
#                 title = json_doc['title']
#                 text = json_doc['text']
#                 try:
#                     author = json_doc['byline']
#                 except KeyError:
#                     author = ''
#                 source = json_doc['doctype']
#                 if date_str < dt.strptime("01-02-2017", "%d-%m-%Y"):
#                     make_txt(title, date, author, source, text)
#             except KeyError:
#                 continue
