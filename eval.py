from enum import Enum

from transformers import BertForSequenceClassification, BertJapaneseTokenizer
from transformers.hf_argparser import DataClass
import torch

MODEL_NAME = 'cl-tohoku/bert-base-japanese-whole-word-masking'

#class Category(Enum):
movement = 0
combat = 1
take = 2
use = 3
find = 4
buy = 5
unknown = 6

#class ObjectType(Enum):
map = 0
box = 1

def eval(text_list, label_list, model, tokenizer):
    encoding = tokenizer(
        text_list,
        padding='longest',
        return_tensors='pt'
    )
    encoding = { k: v for k, v in encoding.items()}
    labels = torch.tensor(label_list)
    with torch.no_grad():
        output = model.forward(**encoding)
    scores = output.logits
    labels_predicted = scores.argmax(-1)
    num_correct = (labels_predicted==labels).sum().item()
    accuracy = num_correct/labels.size(0)

    print('size:')
    print(scores.size())
    print('predicted labels:')
    print(labels_predicted)
    print('accuracy:')
    print(accuracy)
    return labels_predicted


def predict_category(text):
    bert_sc_category = BertForSequenceClassification.from_pretrained('./model1_transformers')
    tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
    encoding = tokenizer(
        text,
        padding='longest',
        return_tensors='pt'
    )
    with torch.no_grad():
        output_category = bert_sc_category.forward(**encoding)
    scores_category = output_category.logits
    label_predicted_category = scores_category.argmax(-1)
    return label_predicted_category


def predict_type(text):
    bert_sc_type = BertForSequenceClassification.from_pretrained('./model2_transformers')
    tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
    encoding = tokenizer(
        text,
        padding='longest',
        return_tensors='pt'
    )
    with torch.no_grad():
        output_type = bert_sc_type.forward(**encoding)
    scores_type = output_type.logits
    label_predicted_type = scores_type.argmax(-1)
    return label_predicted_type


def main():
    text_list = ["ドミノを倒します。", "プリンがあります。", "大阪に行くます。", "スライムがいます。", "HPポーションを買う。", "ポーションを使用する。"]
    label_list1 = [
        unknown,
        unknown,
        movement,
        unknown,
        buy,
        use
    ]

    label_list2 = [
        map,
        map,
        map,
        map,
        map,
        box
    ]
    bert_sc1 = BertForSequenceClassification.from_pretrained('./model1_transformers')
    bert_sc2 = BertForSequenceClassification.from_pretrained('./model2_transformers')
    tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME)
    eval(text_list, label_list1, bert_sc1, tokenizer)
    print('-----------------------------')
    eval(text_list, label_list2, bert_sc2, tokenizer)

if __name__ == "__main__":
    main()
