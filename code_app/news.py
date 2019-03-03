from textblob import TextBlob
import requests
from bs4 import BeautifulSoup
from langdetect import detect
# import matplotlib.pyplot as plt
# from matplotlib import style

# style.use('fivethirtyeight')
# fig = plt.figure()

xs = []
ys = []
news_list = []

class Analysis():
    def __init__(self, term):
        self.term = term
        self.subjectivity = 0
        self.sentiment = 0

        self.url = 'https://www.google.com/search?q={0}&source=lnms&tbm=nws'.format(self.term)

    def run(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        headline_results = soup.find_all('div', class_='st')
        headline_papers = soup.find_all('div', class_='slp')
        
        for h,p in zip(headline_results, headline_papers):
            blob = TextBlob(h.get_text())
            lang = detect(h.get_text())
            if lang != "en":
                continue
            head = p.get_text()
            senti = blob.sentiment.polarity
            sub = blob.sentiment.subjectivity
            xs.append(senti)
            ys.append(head)
            news_list.append((h.get_text(), senti))
            # print(blob, 'from', head, '   Subjectivity:', sub, '   Sentiment:', senti)
            self.sentiment += senti / len(headline_results)
            self.subjectivity += sub / len(headline_results)
        return news_list
            
#v = input('Enter the sentiment you need: ')
a = Analysis('USA stocks')
a.run()
#print(a.term, '   Avg. Subjectivity:', a.subjectivity, '   Avg. Sentiment:', a.sentiment)

# plt.bar(ys, xs)
# plt.show()
