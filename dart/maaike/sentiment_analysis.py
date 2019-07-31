from pattern.nl import sentiment, pluralize, parse, split
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

file = "C:\\Users\\Sanne\\Google Drive\\Maaike - scriptie\\output\\output_eerste_patronen.xlsx"
df = pd.read_excel(file, sheetname='Sheet1')

contents = df.iloc[:, 2]
contents = contents.dropna()

total = 0
for index, row in contents.iteritems():
    s = sentiment(row)
    total = total + s[0]
    # print(row)
    # print("Sentiment: "+str(s[0]) + " Subjectivity: "+str(s[1]))
    s = parse(row)
    # for sentence in split(s):
    #     print(sentence)
    #     for chunk in sentence.chunks:
    #         print(chunk.type, [(w.string, w.type) for w in chunk.words])
    # print()
print(total/len(contents))
