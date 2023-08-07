import transformers
from datasets import Dataset
import pandas as pd
from transformers import TrainingArguments, Trainer
import torch
import argparse
from utils import merge_article_title_and_body_into_one_for_model_input
from consts import *


def preprocess_function(examples, context_size):
    """
    preprocesses data for training into the input format expected by the model
    :param examples: data examples
    :param context_size: max number of tokens for padding purposes (represents the length of context)
    :return: model inputs
    """
    inputs = [ex for ex in examples[MODEL_INPUT_COLUMN_NAME]]
    targets = [ex for ex in examples[LABEL_COLUMN_NAME]]
    model_inputs = tokenizer(inputs, max_length=context_size, padding=PADDING, truncation=True)
    labels = tokenizer(targets, max_length=context_size, padding=PADDING, truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def load_datasets():
    """
    loads train and validation datasets from csv
    :return: Dataset objects representing training and validation data
    """
    train = pd.read_csv(TRAIN_CSV_PATH)
    val = pd.read_csv(VALIDATION_CSV_PATH)

    data_train = Dataset.from_pandas(merge_article_title_and_body_into_one_for_model_input(train))
    data_val = Dataset.from_pandas(merge_article_title_and_body_into_one_for_model_input(val))
    return data_train, data_val


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', '-m', type=str, help='name of model')
    parser.add_argument('--context_size', '-c', type=int, help='size of context')
    parser.add_argument('--batch_size', '-b', type=int, help='size of batch')
    parser.add_argument('--num_epochs', '-e', type=int, help='num epochs')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()

    data_train, data_val = load_datasets()
    model = transformers.MT5ForConditionalGeneration.from_pretrained(MT5_MODELS_DICT[args.model_name])
    tokenizer = transformers.MT5Tokenizer.from_pretrained(MT5_MODELS_DICT[args.model_name])

    train_dataset = data_train.map(preprocess_function, batched=True, desc="Running tokenizer",
                                   fn_kwargs={"context_size": args.context_size})
    val_dataset = data_val.map(preprocess_function, batched=True, desc="Running tokenizer",
                               fn_kwargs={"context_size": args.context_size})

    training_args = TrainingArguments(output_dir='.',
                                      evaluation_strategy="epoch",
                                      save_strategy="no",
                                      num_train_epochs=args.num_epochs,
                                      per_device_train_batch_size=args.batch_size)

    trainer = Trainer(model=model,
                      args=training_args,
                      train_dataset=train_dataset,
                      eval_dataset=val_dataset,
                      tokenizer=tokenizer)
    trainer.train()
    torch.save(model.state_dict(),
               f'finetuned_MT5_context_{args.context_size}_batch_size_{args.batch_size}_epochs_{args.num_epochs}.pt')
