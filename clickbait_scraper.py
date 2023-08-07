import re
import html
import json
import urllib
from consts import *
from tqdm import tqdm
from datetime import datetime
from facebook_page_scraper import Facebook_scraper
from facebook_page_scraper.element_finder import Finder
from facebook_page_scraper.driver_utilities import Utilities
from facebook_page_scraper.driver_initialization import Initializer


class ClickbaitScraper(Facebook_scraper):
    """
    Wrapper class for Facebook_scraper class to scrape clickbait posts from a page
    """

    def __init__(self, num_posts=10):
        super().__init__(AMLK_PAGE_NAME, num_posts, browser='firefox')
        self.__data_dict = {}
        self.__layout = None
        self.__extracted_post = set()

    def __start_driver(self):
        """
        changes the class member __driver value to driver on call
        """
        self.__driver = Initializer(self.browser, self.proxy, self.headless).init()

    def __handle_popup(self, layout):
        try:
            if layout == "old":
                # if during scrolling any of error or signup popup shows
                Utilities._Utilities__close_error_popup(self.__driver)
                Utilities._Utilities__close_popup(self.__driver)
            elif layout == "new":
                Utilities._Utilities__close_modern_layout_signup_modal(
                    self.__driver)
                Utilities._Utilities__close_cookie_consent_modern_layout(
                    self.__driver)
        except Exception as ex:
            print(f"Error at handle_popup : {ex}")

    def get_external_link(self, post):
        """
        gets the external link from a post
        :param post: post element
        :return: external link string
        """
        html_text = post.get_attribute("innerHTML")
        link = re.search(LINK_PATTERN, html_text).group(1)
        return html.unescape(urllib.parse.unquote(link))

    def get_bait(self, post):
        """
        gets the clickbait title from a post
        :param post: post element
        :return: clickbait string
        """
        html_text = post.get_attribute("innerHTML")
        try:
            res = re.findall(BAIT_PATTERN_1, html_text)
            assert len(res) > 1
            bait = html.unescape(res[-1])
            if bait == '':
                res = re.findall(BAIT_PATTERN_2, html_text)
                assert len(res) > 1
                bait = html.unescape(res[-1])
            return bait
        except:
            res = re.findall(BAIT_PATTERN_3, html_text)
            if len(res) == 0:
                raise Exception("No bait found")
            bait = html.unescape(res[0])
            return bait

    def __remove_duplicates(self, all_posts):
        """
        takes a list of posts and removes duplicates from it and returns the list
        """
        if len(self.__extracted_post) == 0:
            self.__extracted_post.update(all_posts)
            return all_posts
        else:
            removed_duplicated = [
                post for post in all_posts if post not in self.__extracted_post]
            self.__extracted_post.update(all_posts)
            return removed_duplicated

    def _find_clickbait_elements(self):
        """
        find elements of posts and add them to data_dict
        """
        all_posts = Finder._Finder__find_all_posts(self.__driver, self.__layout)
        all_posts = self.__remove_duplicates(all_posts)
        for post in all_posts:
            try:
                status, post_url, link_element = Finder._Finder__find_status(post, self.__layout)
                if post_url is None:
                    continue
                post_content = Finder._Finder__find_content(post, self.__driver, self.__layout)
                external_link = self.get_external_link(post)
                bait = self.get_bait(post)

                self.__data_dict[status] = {
                    "content": post_content,
                    "post_url": post_url,
                    "ext_link": external_link,
                    "bait": bait
                }
            except Exception as ex:
                print(ex)

    def get_clickbaits(self):
        """
        Scrolls down the page and extracts clickbait titles and links
        :return: dictionary of clickbait titles and links
        """
        self.__start_driver()
        self.__driver.get(self.URL)
        Finder._Finder__accept_cookies(self.__driver)
        self.__layout = Finder._Finder__detect_ui(self.__driver)
        Utilities._Utilities__close_error_popup(self.__driver)
        Utilities._Utilities__wait_for_element_to_appear(self.__driver, self.__layout)
        Utilities._Utilities__scroll_down(self.__driver, self.__layout)
        self.__handle_popup(self.__layout)

        pb = tqdm(total=self.posts_count)
        while len(self.__data_dict) <= self.posts_count:
            pb.n = min(len(self.__data_dict), self.posts_count)
            pb.refresh()
            self.__handle_popup(self.__layout)
            self._find_clickbait_elements()
            Utilities._Utilities__scroll_down(self.__driver, self.__layout)
        pb.n = min(len(self.__data_dict), self.posts_count)
        pb.refresh()
        pb.close()
        Utilities._Utilities__close_driver(self.__driver)
        return self.__data_dict


def save_clickbaits(data_dir, num_posts):
    """
    Scrapes this.is.amlk and saves clickbaits in a json file
    :param data_dir: directory to save the json file
    :param num_posts: number of posts to scrape
    """
    scraper = ClickbaitScraper(num_posts)
    data = scraper.get_clickbaits()
    date = datetime.now().strftime("%Y%m%d%H%M%S")
    with open(f'{data_dir}/{date}.json', 'w') as f:
        json.dump(data, f, indent=3, ensure_ascii=False)
