import urllib3
from bs4 import BeautifulSoup
import requests
import os
import csv
import unicodedata
import pandas as pd


SUFFIXES = ['', 'latest', 'archive/2000', 'archive/2001', 'archive/2002', 'archive/2003', 'archive/2004', 'archive/2005', 'archive/2006', 'archive/2007', 'archive/2008', 'archive/2009', 'archive/2010', 'archive/2011', 'archive/2012', 'archive/2013', 'archive/2014', 'archive/2015', 'archive/2016', 'archive/2017', 'archive/2018', 'archive/2019']


def get_links_for_tag(tag, suffixes=SUFFIXES):
    url = 'https://medium.com/tag/' + tag
    urls = [url + '/' + s for s in suffixes]
    links = []  
    for url in urls:
        data = requests.get(url)
        soup = BeautifulSoup(data.content, 'html.parser')
        articles = soup.findAll('div', {"class": "postArticle-readMore"})
        for i in articles:
            links.append(i.a.get('href'))
    return links


def get_articles(links, text=True, include_link=True, include_title=True, 
                 include_author=False, include_claps=False, 
                 include_reading_time=False, include_tags=False):
    
    articles = []
    for link in links:
        try:
            article = {}
            data = requests.get(link)
            soup = BeautifulSoup(data.content, 'html.parser')
            
            if include_title:
                title = soup.findAll('title')[0]
                title = title.get_text()
                article['title'] = unicodedata.normalize('NFKD', title)
              
            if include_author:
                author = soup.findAll('meta', {"property": "author"})[0]
                author = author.get('content')
                article['author'] = unicodedata.normalize('NFKD', author)
              
            if include_claps:
                claps = soup.findAll('button', 
                                     {"data-action":"show-recommends"})[0].get_text()
                article['claps'] = unicodedata.normalize('NFKD', claps)
              
            if include_link:
                article['link'] = link
            
            if include_reading_time:
                reading_time = int(soup.findAll('span', 
                                                {"class":"readingTime"})[0].get('title').split()[0])
                article['reading_time'] = reading_time
              
            if include_tags:
                tags = []
                tags_ul = soup.findAll('ul', {"class": "tags"})[0]
                for li in tags_ul.findAll('li'):
                    tags.append(li.find('a').get_text())
                article["tags"] = tags
            
            paras = soup.findAll('p')
            text = ''
            nxt_line = '\n'
            for para in paras:
                text += unicodedata.normalize('NFKD',para.get_text()) + nxt_line
            article['text'] = text
            
            articles.append(article)
            
        except KeyboardInterrupt:
            print('Exiting')
            os._exit(status = 0)
        except Exception as e:
            # for other exceptions 
            print(f"Exception while scraping {link} : {e}")
            continue
    return articles


def save_articles(articles, csv_file,  is_write = True):
    csv_columns = ['author', 'claps', 'reading_time', 'link', 'title', 'text']
    print(csv_file)
    if is_write:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter='|')
            writer.writeheader()
            for data in articles:
                writer.writerow(data)
            csvfile.close()
    else:
        with open(csv_file, 'a+') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns,  delimiter='|')
            for data in articles:
                writer.writerow(data)
            csvfile.close()


def main():
    is_write = True
    tags = input('Write tags in space separated format.\n')
    tags = tags.split(' ')
    file_name = input('Write destination file name.\n')
    
    if len(file_name.split('.')) == 1:
        file_name += '.csv'
        
    for tag in tags:
        links = get_links(tag)
        articles = get_article(links)
        save_articles(articles, file_name, is_write)
        is_write = False
        
    # remove duplicates
    articles = pd.read_csv(file_name, file_name, delimiter='|')
    articles = articles.drop_duplicates()
    articles.to_csv(file_name, sep='|', index=False)
    
if __name__ == '__main__':
    main()
