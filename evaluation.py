import argparse
import json
import os
import numpy as np
import pandas as pd
from nltk.translate.bleu_score import sentence_bleu
from evaluate import load
from rouge import Rouge
from utils import merge_article_title_and_body_into_one_for_model_input, load_model_and_tokenizer, \
    remove_bad_tokens_from_model_output
from consts import *


def calc_avg_bleu_score(references, predictions, tokenizer):
    """
    calculates the BLEU score for each prediction (based on unigram only because of short labels)
    :param references: the references/labels
    :param predictions: the predictions
    :param tokenizer: not used in this function
    :return: average BLEU score over all examples, and list of individual BLEU scores for each example
    """
    blue_scores = [sentence_bleu([r.split()], p.split(), weights=(1, 0, 0, 0)) for r, p in zip(references, predictions)]
    return np.mean(blue_scores), blue_scores


def calc_avg_rouge_scores(references, predictions, tokenizer):
    """
    calculates the ROUGE scores (rouge-1, rouge-2, rouge-l) for each prediction (p, r, f)
    :param references: the references/labels
    :param predictions: the predictions
    :param tokenizer: not used in this function
    :return: average ROUGE scores over all examples, and list of individual ROUGE scores for each example
    """
    hyps, refs = map(list, zip(*[[predictions[i], references[i]] for i in range(len(references))]))
    rouge = Rouge()
    all_scores = rouge.get_scores(hyps, refs, avg=False)
    avg_score = rouge.get_scores(hyps, refs, avg=True)
    return avg_score, all_scores


def calc_avg_BERTscore(references, predictions, tokenizer):
    """
    calculates the BERTscore for each prediction (p, r, f)
    :param references: the references/labels
    :param predictions: the predictions
    :param tokenizer: the tokenizer used
    :return: average BERTscore score over all examples, and list of individual BERTscores for each example
    """
    bertscore = load("bertscore")
    all_scores = bertscore.compute(predictions=predictions, references=references, lang="he")
    avg_score = {'f1': np.mean(all_scores['f1']), 'p': np.mean(all_scores['precision']),
                 'r': np.mean(all_scores['recall'])}
    return avg_score, all_scores


eval_metric_name_to_func_dict = {'bleu': calc_avg_bleu_score,
                                 'rouge': calc_avg_rouge_scores,
                                 'BERTscore': calc_avg_BERTscore}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', '-m', type=str, help='path to the model to evaluate')
    parser.add_argument('--model_name', '-n', type=str, help='name of pretrained model')
    parser.add_argument('--output_prefix', '-p', type=str, help='name of pretrained model')
    parser.add_argument('--test_data_path', '-t', type=str, help='path to the test data to evaluate on')
    parser.add_argument('--output_path', '-o', type=str, help='path to output dir')
    parser.add_argument('--is_baseline', action="store_true")
    args = parser.parse_args()
    return args


def generate_predictions(model, tokenizer, data_path):
    """
    generates model predictions for all examples in the data
    :param model: the model
    :param tokenizer: the tokenizer
    :param data_path: path to data csv
    :return: predictions, references and titles (aligned)
    """
    test_df = merge_article_title_and_body_into_one_for_model_input(pd.read_csv(data_path))
    references = test_df[LABEL_COLUMN_NAME]
    titles = test_df[ARTICLE_TITLE_COLUMN_NAME]
    predictions = []
    for i in range(len(references)):
        context = test_df[MODEL_INPUT_COLUMN_NAME][i]
        features = tokenizer([context], return_tensors='pt')
        output = model.generate(input_ids=features[MODEL_INPUT_IDS].to('cuda'),
                                attention_mask=features[MODEL_ATTENTION_MASK].to('cuda'),
                                max_length=MAX_GENERATION_LENGTH)
        decoded_output = tokenizer.decode(output[0], skip_special_tokens=True)
        predictions.append(remove_bad_tokens_from_model_output(decoded_output))
    return predictions, references, titles


def run_all_eval_metrics(predictions, references, tokenizer):
    """
    runs all evaluation metrics' functions on the given references and predictions
    :param predictions: the predictions
    :param references: the references
    :param tokenizer: the tokenizer (needed for BERTscore)
    :return: average evaluation metrics' scores and individual scores for each example
    """
    eval_metric_avg_scores, eval_metric_all_scores = {}, {}
    for metric_name in eval_metric_name_to_func_dict:
        avg_score, all_scores = eval_metric_name_to_func_dict[metric_name](references, predictions, tokenizer)
        eval_metric_avg_scores[metric_name] = avg_score
        eval_metric_all_scores[metric_name] = all_scores
    return eval_metric_avg_scores, eval_metric_all_scores


def write_out_eval_results(eval_results, output_path, output_prefix):
    """
    writes out evaluation results into json file
    :param eval_results: evaluation results
    :param output_path: path to output dir
    :param output_prefix: prefix for json name
    """
    with open(os.path.join(output_path, f'eval_results_{output_prefix}.json'), 'w+', encoding='utf8') as f:
        json.dump(eval_results, f)


def create_predictions_df(predictions, references, titles, eval_metric_all_scores):
    """
    creates predictions dataframe with the evaluation metrics' scores (specifically BERTscore f1, BLEU, and ROUGE-L f1)
    :param predictions: the predictions
    :param references: the references
    :param titles: matching article titles for the references
    :param eval_metric_all_scores: all evaluation metrics' individual scores for all examples
    :return: predictions dataframe
    """
    predictions_df = pd.DataFrame({'reference': references, 'prediction': predictions,
                                   'title': titles})
    predictions_df['BERTscore_f1'] = eval_metric_all_scores['BERTscore']['f1']
    predictions_df['bleu'] = eval_metric_all_scores['bleu']
    predictions_df['ROUGE_L_f1'] = [eval_metric_all_scores['rouge'][i]['rouge-l']['f'] for i in range(len(predictions))]
    return predictions_df


def write_out_all_predictions_to_csv(predictions_df, output_path, output_prefix):
    """
    writes out predictions dataframe to csv file
    :param predictions_df: predictions dataframe
    :param output_path: output dir path
    :param output_prefix: csv name prefix
    """
    predictions_df.to_csv(os.path.join(output_path, f'predictions_{output_prefix}.csv'), encoding='utf8')


def write_out_examples_with_lowest_BERTscore_to_csv(predictions_df, output_path, output_prefix, k=20):
    """
    writes out k predictions with lowest BERTscore from dataframe to csv file
   :param predictions_df: predictions dataframe
    :param output_path: output dir path
    :param output_prefix: csv name prefix
    :param k: number of predictions to write out
    """
    lowest_score_df = predictions_df.sort_values(by=['BERTscore_f1'])[:k]
    lowest_score_df.to_csv(os.path.join(output_path, f'predictions_{output_prefix}_lowest_BERScore_{k}.csv'),
                           encoding='utf8')


def main(model_path, pretrain_model_name, is_baseline, output_prefix, test_data_path, output_path):
    model, tokenizer = load_model_and_tokenizer(model_path, pretrain_model_name, is_baseline)
    predictions, references, titles = generate_predictions(model, tokenizer, test_data_path)
    eval_metric_avg_scores, eval_metric_all_scores = run_all_eval_metrics(predictions, references, tokenizer)
    write_out_eval_results(eval_metric_avg_scores, output_path, output_prefix)
    predictions_df = create_predictions_df(predictions, references, titles, eval_metric_all_scores)
    write_out_all_predictions_to_csv(predictions_df, output_path, output_prefix)
    write_out_examples_with_lowest_BERTscore_to_csv(predictions_df, output_path, output_prefix)


if __name__ == '__main__':
    args = parse_args()
    main(args.model_path, args.model_name, args.is_baseline, args.output_prefix, args.test_data_path, args.output_path)
