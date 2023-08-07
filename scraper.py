import os
import json
import requests
import argparse
import pandas as pd
from tqdm import tqdm
from glob import glob
from consts import *
from bs4 import BeautifulSoup
from selenium import webdriver
from clickbait_scraper import save_clickbaits
from selenium.webdriver.chrome.options import Options
from news_scrapers.hebrew.israelhayom import IsraelhayomScraper


def create_browser():
    """
    creates a browser for scraping
    :return: a selenium Chrome browser
    """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    return browser


def transform_url(url):
    """
    checks if the url is shortened, if so it corrects it
    :param url: string url
    :return: a long version of the url
    """
    if SHORTEN_CODE in url:
        url = requests.head(url).headers['location']
    url = url.replace('http:', 'https:')
    url = url.split('?')[0].split('#')[0]
    return url


def scrape_from_tmi(url):
    """
    scrapes the article from TMI
    :param url: url to an article in TMI
    :return: article title, article body
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    cur_title = soup.select_one('title').text.strip()
    all_script = soup.find_all('script', {'type': 'application/ld+json'})
    for script in all_script:
        script_text = script.getText()
        if "articleBody" in script_text:
            start_inx = script_text.find("articleBody")
            cur_body = script_text[start_inx:]
            end_ind = cur_body.find("\n")
            cur_body = cur_body[:end_ind].strip('"articleBody":')
            return cur_title,cur_body
    raise Exception("No article body found")


def scrape_from_israelhayom(url, browser):
    """
    scrapes the article from Israel Hayom
    :param url: url to an article in Israel Hayom
    :return: article title, article body
    """
    scraper = IsraelhayomScraper()
    html = scraper.fetcher.fetch(url)
    article = scraper._process_page((html, url))[0]
    if len(article.text) > 0:
        return article.title, article.text
    browser.get(url)
    html = scraper.fetcher.fetch(url)
    article = scraper._process_page((html, url))[0]
    assert len(article.text) > 0, "No text found"
    return article.title, article.text


def scrape_from_mako(url):
    """
    scrapes the article from Mako
    :param url: url to an article in Mako
    :return: article title, article body
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    all_p = soup.find_all('p', attrs={'class': 'Standard'})
    text = ' '.join([a.text for a in all_p])
    body = text
    if len(body) < 20:
        text = ""
        p_tags = soup.find_all('p', attrs=None)
        for tag in p_tags:
            text = text + tag.get_text()
        body = text.replace('\n\n','')
    script = soup.find_all('script', {'type': 'application/ld+json'})[0]
    script_text = script.getText()
    start_inx = script_text.find("headline")
    cur_title = script_text[start_inx:]
    end_ind = cur_title.find("\n")
    cur_title = cur_title[:end_ind].strip('"headline":')
    return cur_title, body


def scrape_from_walla(url):
    """
    scrapes the article from Walla
    :param url: url to an article in Walla
    :return: article title, article body
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    text = ' '.join([a.text.strip() for a in soup.find_all('p', attrs={'class': 'article_speakable'})[1:]])
    assert len(text) > 0, "No text found"
    title = soup.select_one('h1').text.strip()
    return title, text


def save_to_csv(output_file, all_titles, all_links, all_bodies):
    """
    saves the data to a csv file
    :param output_file: output path to csv file
    :param all_titles: list of titles
    :param all_links: list of links
    :param all_bodies: list of article contents
    """
    data = {'Title': all_titles,
            'Body': all_bodies, 'Link': all_links}
    df = pd.DataFrame(data).drop_duplicates()
    df.to_csv(output_file, encoding='utf-8-sig')


def load_data(data_dir):
    """
    loads the links from the json files
    :param data_dir: path to a posts directory
    :return: a list of post links
    """
    data = dict()
    paths = glob(f'{data_dir}/*.json')
    for path in paths:
        with open(path, 'r') as f:
            data.update(json.load(f))
    return [post['ext_link'] for post in data.values()]


def get_articles(links):
    """
    scrapes the articles from the links
    :param links: list of links
    :return: list of titles, list of links, list of article contents
    """
    all_titles = []
    all_bodies = []
    all_links = []
    browser = create_browser()
    for link in tqdm(links):
        cur_url = transform_url(link)
        try:
            if TMI_PREFIX in cur_url:
                title, body = scrape_from_tmi(cur_url)
            elif ISRAELHAYOM_PREFIX in cur_url:
                title, body = scrape_from_israelhayom(cur_url, browser)
            elif MAKO_PREFIX in cur_url:
                title, body = scrape_from_mako(cur_url)
            elif WALLA_PREFIX in cur_url:
                title, body = scrape_from_walla(cur_url)
            else:
                continue
            all_titles.append(title)
            all_bodies.append(body)
            all_links.append(link)
        except Exception as e:
            print(f'Error when scraping article from {cur_url}, error: {e}')
    return all_titles, all_links, all_bodies


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', '-d', type=str, help='path to posts dir', required=True)
    parser.add_argument('--output-file', '-o', type=str, help='output csv path', required=True)
    parser.add_argument('--num-links', '-n', type=int, help='number of links to scrape', default=100)
    parser.add_argument('--save-clickbaits', '-s', action='store_true', help='get new clickbaits', default=False)
    parser.add_argument('--num-posts', '-p', type=int, help='number of posts to scrape (only with --save-clickbaits)', default=100)
    args = parser.parse_args()
    return args.data_dir, args.output_file, args.num_links, args.save_clickbaits, args.num_posts


if __name__ == '__main__':
    data_dir, output_file, num_links, is_save_clickbaits, num_posts = parse_args()
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if is_save_clickbaits:
        save_clickbaits(data_dir, num_posts)
    links = load_data(data_dir)[:num_links]
    all_titles, all_links, all_bodies = get_articles(links)
    save_to_csv(output_file, all_titles, all_links, all_bodies)
