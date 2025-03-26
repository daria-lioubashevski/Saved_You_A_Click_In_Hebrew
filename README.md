# Saved You a Click In Hebrew

A real-world dataset for training and evaluating question answering models in Hebrew.
Built by combining Israeli news sources with TL;DR-style posts from Facebook.
👉 [View on Hugging Face 🤗](https://huggingface.co/datasets/daria-lioub/heb_amlk_for_QA)

The repository contains:
1. Code for recreating and expanding the dataset from news sources and TL;DR-style posts.
2. Code for fine-tuning and evaluating language models on the QA task.
   
[📝Read the full project description (PDF)](project_description.pdf)


# List of Contents

_Data gathering_:
* clickbait_scraper.py - wrapper for facebook_scraper which handles the logic of scraping the posts' text, links and clickbait titles
* scraper.py - scrapes Facebook posts and articles from different news websites
* data_preprocessing.py - filters and cleans the data

_Training_:
* finetune_pipeline.py - fine-tunes a pre-trained model with appropriate hyper-parameters

_Evaluation_:
* evaluation.py - generates predictions and preforms evaluation on a pre-trained/fine-tuned model 
* annotators_guide.txt - guide for human annotation

_Misc._:
* utils.py - contains general utility functions
* consts.py - constants needed for the project

