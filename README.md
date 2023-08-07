**Saved You A Click In Hebrew**

The term "clickbait" refers to a common practice of presenting a title of an article next to a link,
with the sole purpose of luring the user into clicking and visiting the article's website. 
To achieve this, these titles often intentionally leave out the most interesting part of the story 
to spark the curiosity of the reader. 
The main goal of this project is to train a LLM that can take a clickbait title and a news article 
body in Hebrew as input, and generate the missing information as output, “saving” the user a click.

We consider this task to be a more generalized variant of abatractive question answering (QA),
where the "question" is a clickbait title of a news article, the text is the the article body and 
the "answer" is the text of the Facebook post containing the missing piece of information from the 
clickbait.

To achieve this goal, we created a first of it's kind (to the best of our knowledge) labeled real-world dataset 
in Hebrew based on posts scraped from the Facebook page “this.is.amlk”
(https://www.facebook.com/this.is.amlk).
This dataset is now publicaly availible on HuggingFace with n=2625 data samples split into train
test with ratio 9:1 respecively (https://huggingface.co/datasets/daria-lioub/heb_amlk_for_QA) 

We then fine-tuned  mT5, a pre-trained sequence-to-sequence multilingual model, in variants small
(300M parameters), base (580M parameters) and large (1.2B parameters) on our dataset for this task, using the 
following template for the input: "question: [clickbait title] context: [article body]”.

<br>

**List Of Contents**

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

