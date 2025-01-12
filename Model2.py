from typing import Dict, List, Tuple, Any
import random
import glob
import re
import unicodedata
from pytorch_lightning.loggers import TensorBoardLogger
from tqdm import tqdm

import torch
from torch.utils.data import DataLoader
from transformers import BertJapaneseTokenizer, BertForSequenceClassification
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping

# 定数の定義
MODEL_NAME = 'cl-tohoku/bert-base-japanese-whole-word-masking' # 日本語BERTモデル名
MAX_LENGTH = 20         # 文章の長さの最大値
TRAIN_BATCH_SIZE = 3    # 訓練データのバッチサイズ
BATCH_SIZE = 16         # 検証データとテストデータのバッチサイズ
NUM_LABELS = 2          # カテゴリー map or box
LEARNING_RATE = 1e-5    # 学習率
MAX_EPOCHS = 10         # 最大エポック数

category_list = [
    "map",     #0
    "box",     #1
]

class TextClassificationDataset:
    def __init__(self, data_dir, categories, tokenizer, max_length):
        self.dataset = []
        for label, category in enumerate(tqdm(categories, desc="Loading data")):
            for file in glob.glob(f'{data_dir}/{category}*'):
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.read().splitlines()
                    for text in lines:
                        if text == "":
                            continue
                        text = self.preprocess(text)
                        encoding = tokenizer(
                            text,
                            max_length=max_length,
                            padding='max_length',
                            truncation=True
                        )
                        encoding['labels'] = label
                        encoding = {k: torch.tensor(v) for k, v in encoding.items()}
                        self.dataset.append(encoding)

    def split_dataset(self, train_ratio: float = 0.6, val_ratio: float = 0.2):
        random.shuffle(self.dataset)
        n = len(self.dataset)
        n_train = int(train_ratio * n)
        n_val = int(val_ratio * n)

        return (
            self.dataset[:n_train],
            self.dataset[n_train:n_train+n_val],
            self.dataset[n_train+n_val:]
        )

    def preprocess(self, text):
        new_text = unicodedata.normalize("NFKC", text)
        new_text = text.lower()
        new_text = re.sub(' ', '', new_text) # 半角スペース削除
        new_text = re.sub('　', '', new_text)# 全角スペース削除
        new_text = re.sub(r'[、，。,.]+', '', new_text) # 符号を削除
        return new_text

class BertForSequenceClassification_pl(pl.LightningModule):
    def __init__(self, model_name, num_labels, lr):
        super().__init__()
        self.save_hyperparameters()
        self.bert_sc = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )

    def training_step(self, batch, batch_idx):
        output = self.bert_sc(**batch)
        loss = output.loss
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True)
        return loss

    def validation_step(self, batch, batch_idx):
        output = self.bert_sc(**batch)
        val_loss = output.loss
        self.log('val_loss', val_loss, on_epoch=True, prog_bar=True)
        return val_loss

    def test_step(self, batch, batch_idx):
        labels = batch.pop('labels')
        output = self.bert_sc(**batch)
        labels_predicted = output.logits.argmax(-1)
        num_correct = (labels_predicted == labels).sum().item()
        accuracy = num_correct/labels.size(0)
        self.log('test_accuracy', accuracy, on_epoch=True)
        return {'test_accuracy': accuracy}

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.hparams.lr)
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.1, patience=2, verbose=True
        )
        return {
            'optimizer': optimizer,
            'lr_scheduler': scheduler,
            'monitor': 'val_loss'
        }

def main():
    # データの準備
    tokenizer = BertJapaneseTokenizer.from_pretrained(MODEL_NAME, mecab_kwargs={"mecab_dic": "ipadic"})
    dataset = TextClassificationDataset('./my_data2', category_list, tokenizer, MAX_LENGTH)
    train_dataset, val_dataset, test_dataset = dataset.split_dataset()

    # データローダーの作成
    train_loader = DataLoader(train_dataset, batch_size=TRAIN_BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

    # モデルの設定
    model = BertForSequenceClassification_pl(
        MODEL_NAME, num_labels=NUM_LABELS, lr=LEARNING_RATE
    )

    # コールバックの設定
    checkpoint_callback = ModelCheckpoint(
        monitor='val_loss',
        dirpath='model2/',
        filename='bert-japanese-{epoch:02d}-{val_loss:.2f}',
        save_top_k=1,
        mode='min'
    )

    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=3,
        mode='min'
    )

    # ロガーの設定
    logger = TensorBoardLogger('logs', name='model2')

    # トレーナーの設定
    trainer = pl.Trainer(
        max_epochs=MAX_EPOCHS,
        callbacks=[checkpoint_callback, early_stopping],
        logger=logger,
        accelerator='auto',
        devices=1
    )

    # モデルの学習
    trainer.fit(model, train_loader, val_loader)

    # テストの実行
    test_result = trainer.test(model, test_loader)[0]

    print(f'Best model path: {checkpoint_callback.best_model_path}')
    print(f'Best validation loss: {checkpoint_callback.best_model_score:.4f}')
    print(f'Test accuracy: {test_result["test_accuracy"]:.4f}')

    # モデルの保存
    model = BertForSequenceClassification_pl.load_from_checkpoint(checkpoint_callback.best_model_path)
    model.bert_sc.save_pretrained('./model2_transformers')

if __name__ == '__main__':
    main()
