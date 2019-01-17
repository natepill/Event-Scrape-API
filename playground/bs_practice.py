from bs4 import BeautifulSoup
import requests
import csv

source = requests.get('http://coreyms.com/').text #grabs text (html) from response object

soup = BeautifulSoup(source, 'lxml')

# article = soup.find('article')

csv_file = open('cms_scrape.csv', 'w')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['headline', 'summary', 'video_link'])

for article in soup.find_all('article'): #Class has "_" because 'class' is an inbuilt keyword
    headline = article.h2.a.text
    print(headline)

    summary = article.find('div', class_='entry-content').p.text
    print(summary)


    try:
        vid_src = article.find('iframe', class_='youtube-player')['src']
        #to get value of an atrrtibute of a tag, we can access that attribute like a dict ^^
        # print(vid_src)

        vid_id = vid_src.split('/')[4]
        vid_id = vid_id.split('?')[0]
        print(vid_id)
        #How to get really specific data like video id ^^
        yt_link = f'https://youtube.com/watch?v={vid_id}'

    except Exception as e:
            yt_link = None

    csv_writer.writerow([headline, summary, yt_link])

csv_file.close()



#
# print(headline)

# with open('simple.html') as html_file:
#     soup = BeautifulSoup(html_file, 'lxml') #opening the html file and specifying the usage of the lxml bodyParser
#
#
# print(soup.prettyify()) #prints html that looks good
#


#find vs find_all: find method gets the first tag that matches the specification
#find_all method returns a list that matches all those arguments
