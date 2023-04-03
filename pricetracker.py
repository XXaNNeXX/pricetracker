import requests
import re
import smtplib
import json
from bs4 import BeautifulSoup

MAIL_ADDRESS = 'anne.hensel.ah@gmail.com'
PASSWORD = 'uuoonzcyosrkgntw'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
}

ARTICLE_FILE = 'articles.json'

def read_json():
    articles = []
    try:
        with open(ARTICLE_FILE, 'r') as file:
            articles = json.load(file)
    except FileNotFoundError as e:
        print(ARTICLE_FILE, 'does not exist')

    except json.decoder.JSONDecodeError as e:
        print('Invalid json file', e.msg, 'in line', e.lineno)

    return articles

def validate_articles(articles):
    valid_articles = []
    for article in articles:
        if('url' not in article or 'target_price' not in article):
            continue

        if('bityl.co' not in article['url'] or type(article['target_price']) is not float):
            continue

        valid_articles.append(article)

    return valid_articles

def parse_price(price_text):
    price_text = price_text.replace('€', '')
    price_text = price_text.replace('EUR', '')
    price_text = price_text.strip()
    price_text = price_text.replace('.', '')
    price_text = price_text.replace(',', '.')
    return float(price_text)

def get_article_details(article):
    url = article['url']

    article['price'] = 0.0
    article['name'] = ''
    if url is not None:
        page = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(page.content, 'html5lib')
        title_span = soup.find('div', class_='js-color-name')
        if title_span is not None:
            article['name'] = title_span.get_text().strip()

        price_span = soup.find('div', class_='discountPrice')
        if price_span is None:
            price_span = soup.find('div', class_='price')
    
        if price_span is not None:
            article['price'] = parse_price(price_span.get_text())
    return article

def send_email(article_details):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(MAIL_ADDRESS, PASSWORD)

    subject=f"{article_details['name']} Sweater von Hessnatur reduziert"
    body=f"{article_details['name']} Sweater jetzt für {article_details['price']} €: {article_details['url']}"

    message = f'Subject: {subject}\n\n{body}'
    server.sendmail(MAIL_ADDRESS, MAIL_ADDRESS, message.encode('utf8'))
    server.quit()

if __name__ == '__main__':
    articles = read_json()
    valid_articles = validate_articles(articles)
    for article in valid_articles:
        article_details = get_article_details(article)
        if (article_details['price'] is not None and article_details['price'] <= article['target_price']):
            send_email(article_details)
