import argparse
import numpy as np
import pandas as pd
from consts import *


def filter_posts_by_length(all_posts_df, max_length=20):
    """
    filters posts by length, keeping only posts that have less than max_length words
    :param all_posts_df: all posts dataframe
    :param max_length: maximum acceptable length of post (in words) 
    :return: filtered dataframe
    """
    all_posts_df['post_split'] = all_posts_df[POST_TEST_COLUMN_NAME].str.split(' ')
    short_post_text_df = all_posts_df[all_posts_df['post_split'].str.len() <= max_length]
    short_post_text_df = short_post_text_df[short_post_text_df['post_split'].str.len() > 0]
    short_post_text_df = short_post_text_df.drop(columns=['post_split'])
    return short_post_text_df


def filter_invalid_article_titles(posts_df):
    """
    filters out posts with invalid article titles (which can happen due to scraping methods)
    :param posts_df: posts dataframe
    :return: filtered posts dataframe
    """
    posts_df = posts_df[posts_df[ARTICLE_TITLE_COLUMN_NAME] != FAILED_TO_OPEN_VAL]
    posts_df = posts_df[posts_df[ARTICLE_TITLE_COLUMN_NAME] != 'None']
    posts_df = posts_df[posts_df[ARTICLE_TITLE_COLUMN_NAME].str.contains(BAD_ART_TITLE_STRINGS_REG) == False]
    return posts_df


def filter_posts_with_bad_strings(posts_df):
    """
    filters out posts which contain "bad" strings (suggesting post is not fit for the task)
    :param posts_df: posts dataframe
    :return: filtered dataframe
    """
    posts_df = posts_df[posts_df[POST_TEST_COLUMN_NAME].str.contains(BAD_POST_TEXT_STRINGS_REG) == False]
    return posts_df.reset_index(drop=True)


def filter_posts_contained_in_art_title(posts_df):
    """
    filters out most posts with text that is mostly contained in the title (suggesting this is not
    a clickbait title)
    :param posts_df: posts dataframe
    :return: filtered dataframe
    """
    good_idxs_mask = np.full(len(posts_df), False)
    for i in range(len(posts_df)):
        art_title = posts_df[ARTICLE_TITLE_COLUMN_NAME][i]
        post_text = posts_df[POST_TEST_COLUMN_NAME][i]
        if post_text in art_title:
            continue
        if " " in post_text:
            post_text_list = post_text.split(" ")
        else:
            post_text_list = [post_text]
        if " " in art_title:
            art_title_list = art_title.split(" ")
        else:
            art_title_list = [art_title]
        post_art_title_overlap = list(set(art_title_list) & set(post_text_list))
        if len(post_art_title_overlap) > MAX_TITLE_POST_TEXT_SIMILAR_FACTOR * len(post_text_list):
            continue
        good_idxs_mask[i] = True
    return posts_df[good_idxs_mask].reset_index(drop=True)


def apply_filters(posts_df):
    """
    applies all filter functions to the posts dataframe
    :param posts_df: posts dataframe
    :return: filtered dataframe
    """
    posts_df = filter_posts_by_length(posts_df)
    posts_df = filter_invalid_article_titles(posts_df)
    posts_df = filter_posts_with_bad_strings(posts_df)
    posts_df = filter_posts_contained_in_art_title(posts_df)
    return posts_df


def clean_post_text(posts_df):
    """
    cleans up the text of the posts in the dataframe
    :param posts_df: posts dataframe
    :return: dataframe with clean posts
    """
    for s in POST_STRINGS_TO_REMOVE:
        posts_df[POST_TEST_COLUMN_NAME] = posts_df[POST_TEST_COLUMN_NAME].str.replace(s, "")
    return posts_df.reset_index(drop=True)


def clean_article_titles(posts_df):
    """
    cleans up the article titles in the dataframe
    :param posts_df: posts dataframe
    :return: dataframe with clean article titles
    """
    for s in NEWSPAPER_NAME_STRINGS + ARTICLE_TITLE_STRINGS_TO_REMOVE:
        posts_df[ARTICLE_TITLE_COLUMN_NAME] = posts_df[ARTICLE_TITLE_COLUMN_NAME].str.replace(s, '')
    return posts_df


def apply_cleaning_funcs(posts_df):
    """
    applies all cleaning functions to the posts dataframe
    :param posts_df: posts dataframe
    :return: cleaned dataframe
    """
    posts_df = clean_article_titles(posts_df)
    posts_df = clean_post_text(posts_df)
    return posts_df


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--posts_csv_path', '-p', type=str, help='path to original posts csv')
    parser.add_argument('--output_path', '-o', type=str, help='desired path for the clean csv')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    orig_posts_df = pd.read_csv(args.posts_csv_path)
    filtered_posts_df = apply_filters(orig_posts_df)
    clean_posts_df = apply_cleaning_funcs(filtered_posts_df)
    clean_posts_df.to_csv(args.output_path)
