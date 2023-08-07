import torch
import transformers
from transformers import MT5ForConditionalGeneration, AutoModelForCausalLM, AutoTokenizer
from consts import *


def merge_article_title_and_body_into_one_for_model_input(df):
    """
    merge article title and body into one text using QA formatting to be used as model input (for each example)
    :param df: dataframe containing all examples
    :return: dataframe with new column representing the model input
    """
    df[MODEL_INPUT_COLUMN_NAME] = None
    for i in range(len(df)):
        df[MODEL_INPUT_COLUMN_NAME][i] = MODEL_INPUT_FORMAT.format(df[ARTICLE_TITLE_COLUMN_NAME][i],
                                                                                 df[BODY_COLUMN_NAME][i])
    return df


def remove_bad_tokens_from_model_output(model_output):
    """
    replaces all bad tokens (known artifacts of mT5) in model output with empty strings
    :param model_output: string representing model output
    :return: model output without the bad tokens
    """
    for token in BAD_TOKENS:
        model_output = model_output.replace(token, '')
    return model_output


def load_model_and_tokenizer(model_state_dict_path, pretrain_model_name, is_baseline=False):
    """
    loads MT5 model weight from given state dict if not baseline, else from pretrained based on model name
    :param model_state_dict_path: path to model state dict
    :param pretrain_model_name: name of pretrained model (e.g. google/mt5-base)
    :param is_baseline: if True loads from pretrained, if False from given state dict
    :return: loaded model and matching tokenizer
    """
    config = transformers.MT5Config.from_pretrained(pretrain_model_name)
    model = MT5ForConditionalGeneration(config=config).to('cuda')
    tokenizer = transformers.MT5Tokenizer.from_pretrained(pretrain_model_name)
    if is_baseline:
        model = transformers.MT5ForConditionalGeneration.from_pretrained(pretrain_model_name).to('cuda')
    else:
        model.load_state_dict(torch.load(model_state_dict_path), strict=False)
    return model, tokenizer