import sys
import os
import unicodedata
import pygame
from typing import List
from enum import Enum
import re

import Building
import Color
from Character import Monster, Player
from Item import HP_Potion, Item, MP_Potion
from Shop import Shop
from Sprite import Sprite
from GameUtils import BOX_POSITION, ITEM_SHOW_COUNT_OFFSET
from TextInput import TextInput
from Building import Building
import eval
from GameConfig import GameConfig
from Character import Goblin
from Character import Slime

class Game:
    """ゲームのメインクラス"""

    def __init__(self) -> None:
        """ゲームの初期化"""
        pygame.init()
        # 環境変数の設定　日本語を入力できるため
        os.environ['SDL_IM_MODULE'] = 'fcitx'   # または'ibus'

        self.setup_display()
        self.setup_game_components()
        self.setup_sprite_group()
        self.setup_map()
        self.setup_characters()

# ゲームロジック
    def setup_display(self) -> None:
        """ディスプレイ関連の設定"""
        pygame.display.set_caption(GameConfig.TITLE)
        self.screen = pygame.display.set_mode(GameConfig.SCREEN_DIMENSIONS)
        self.font = pygame.font.Font(None, 80)
        self.text_font = pygame.font.SysFont(None, 25)
        self.nlp_result_font = pygame.font.SysFont("notosansmonocjkjp", 25)
        self.eval_result = self.nlp_result_font.render("", True, Color.WHITE)
        self.action_result = self.nlp_result_font.render("", True, Color.WHITE)

    def setup_game_components(self) -> None:
        """ゲームコンポーネントの設定"""
        self.clock = pygame.time.Clock()
        self.tmr = 0
        self.running = True

        # テキスト入力
        pygame.key.start_text_input()
        # テキストボックス
        self.text_input_box = TextInput(100, 550, 200, 50)
        self.nlp_text = ""
        self.start_eval = False

    def setup_characters(self) -> None:
        """キャラクターの初期設定"""
        self.player = Player(32, 32, self)
        hp_potion = HP_Potion(count=5)
        self.player.buy(item=hp_potion, shop=self.shop)
        for item in self.player.item_box:
            if isinstance(item, Item):
                self.all_sprites.add(item.sprite)
                #print(len(self.all_sprites))

        self.monsters: List[Monster] = []
        self.init_monsters()
        print('現在マップにいるモンスター:')
        for monster in self.monsters:
            print(f"[{monster.name}]")

    def setup_map(self):
        """マップ上にあるオブジェクトを初期化"""
        self.buildings: List[Building] = []
        self.shop = Shop(name="商店", x=200, y=200, game=self, item_type_list=[HP_Potion, MP_Potion])
        if isinstance(self.shop, Building):
            self.buildings.append(self.shop)
        print('現在マップにある建造物:')
        for building in self.buildings:
            print(f"[{building.name}]")
        print("商店にHPポーションがありますか? :", self.shop.has_item(HP_Potion))

    def setup_sprite_group(self) -> None:
        """spriteグループの初期設定"""
        self.all_sprites = pygame.sprite.Group()

    def update(self) -> None:
        """メインゲームループ"""
        self.handle_events()
        self.render()
        self.maintain_frame_rate()

    def handle_events(self) -> None:
        """イベント処理"""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_u:
                    self.player.use(index=0)

            self.text_input_box.handle_event(event, self)
            if self.nlp_text != "":
                self.eval_text(self.nlp_text)

    def update_game_state(self) -> None:
        """ゲーム状態の更新"""
        self.tmr += 1
        for monster in self.monsters:
            if not monster.alive:
                self.monsters.remove(monster)
                continue
            monster.update()
        for building in self.buildings:
            building.update()
        self.player.update()
        self.all_sprites.update()
        self.all_sprites.draw(self.screen)

        if self.player.is_attack_action():
            self.player.move_to(self.player.target)
            self.player.attack(self.player.target)
        if self.player.is_move_action():
            self.player.move_to(self.player.target)

    def render(self) -> None:
        """画面描画"""
        self.screen.fill(Color.BLACK)
        # アイテムボックスとゲーム画面を分ける線
        pygame.draw.rect(self.screen, Color.WHITE, (0, 540, 800, 1))
        self.render_box()
        self.update_game_state()
        self.text_input_box.draw(self.screen)

        if self.start_eval:
            self.screen.blit(self.eval_result, (300, 40))
            self.screen.blit(self.action_result, (300, 70))
        pygame.display.update()

    def maintain_frame_rate(self) -> None:
        """フレームレートの維持"""
        self.clock.tick(60)

    def shutdown(self) -> None:
        """ゲームの終了処理"""
        self.running = False
        pygame.quit()
        sys.exit()

    def init_monsters(self) -> None:
        """モンスターの初期配置"""
        self.add_monster(Goblin(500, 500, self))
        self.add_monster(Goblin(300, 400, self))
        self.add_monster(Slime(400, 300, self))

    def add_monster(self, monster: Monster) -> None:
        """モンスターの追加"""
        self.monsters.append(monster)

    def render_box(self):
        for idx, item in enumerate(self.player.item_box):
            if isinstance(item, Item):
                count = item.check_count()
                sprite = item.sprite
                text = self.text_font.render(str(count), True, Color.WHITE)
                self.screen.blit(text, (BOX_POSITION[idx][0] + ITEM_SHOW_COUNT_OFFSET,
                                        BOX_POSITION[idx][1] + ITEM_SHOW_COUNT_OFFSET))


# nlp部分
    def eval_text(self, text):
        """入力されたテキストをモデルで評価"""
        self.eval_init()
        self.start_eval = True
        if text == None or text == "":
            return
        text = self.text_preprocess(text)
        label_category = eval.predict_category(text)
        label_type = eval.predict_type(text)

        category_message = ""
        type_message = ""
        categories = ["移動", "戦闘", "採取", "使用", "捜索", "購入", "未知"]
        types = ["マップ", "ボックス"]
        label_category = label_category[0].item()
        label_type = label_type[0].item()
        category_message = categories[label_category]
        type_message = types[label_type]
        print("category:", category_message, "type:", type_message)
        output_message = "category:" + category_message + " type:" + type_message
        self.eval_result = self.nlp_result_font.render(output_message, True, Color.WHITE)

        if label_category == eval.movement and label_type == eval.map:
            txt = ""
            for i, monster in enumerate(self.monsters):
                if monster.name in text:
                    self.player.target = self.monsters[i]
                    self.player.action_type = "movement"
                    txt = f"{monster.name}:移動"
                    print(txt)
                    self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                    return
            for i, building in enumerate(self.buildings):
                if building.name in text:
                    self.player.target = self.buildings[i]
                    self.player.action_type = "movement"
                    txt = f"{building.name}:移動"
                    print(txt)
                    self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                    return
            print('オブジェクトがマップ上に存在しません！')
            txt = 'オブジェクトがマップ上に存在しません！'
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return

        elif label_category == eval.combat and label_type == eval.map:
            for i, monster in enumerate(self.monsters):
                if monster.name in text:
                    self.player.target = self.monsters[i]
                    self.player.action_type = "combat"
                    return
            print('モンスターがマップにいませんでした。')
            txt = 'モンスターがマップにいませんでした。'
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return True

        elif label_category == eval.buy and label_type == eval.box:
            name_list = ['mp', 'mpポーション', 'mp薬']
            item = MP_Potion
            if self.buy_item_with_eval(text, item, name_list):
                return True

            name_list = ['hp', 'hpポーション', 'ポーション', 'hp薬', '薬']
            item = HP_Potion
            if self.buy_item_with_eval(text, item, name_list):
                return True

            print('このオブジェクトは購入できません。')
            txt = 'このオブジェクトは購入できません。'
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return False

        elif label_category == eval.take and label_type == eval.map:
            name_list = ['うさぎ', 'ウサギ', '野菜', 'おおかみ', 'オオカミ', '狼']
            for name in name_list:
                if name in text:
                    txt = f"{name}を採取した"
                    print(txt)
                    self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                    return True
            txt = "採取できませんでした"
            print(txt)
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return False

        elif label_category == eval.use and label_type == eval.box:
            name_list = ['mp', 'mpポーション', 'mp薬']
            item = MP_Potion
            if self.use_position_with_eval(text, item, name_list):
                return True

            if 'mp' in text:
                txt = 'MPポーションがありません'
                print(txt)
                self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                return False

            name_list = ['hp', 'hpポーション', 'ポーション', 'hp薬', '薬']
            item = HP_Potion
            if self.use_position_with_eval(text, item, name_list):
                return True

            if 'hp' in text:
                txt = 'HPポーションがありません'
                print(txt)
                self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                return False

            txt = '使用できません。'
            print(txt)
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return False

        elif label_category == eval.find:
            in_box, on_map = False, False
            txt = ""
            # map上で探してみる
            for i, monster in enumerate(self.monsters):
                name = self.text_preprocess(monster.name)
                if name in text:
                    txt = f"{monster.name}はマップ上にいます。"
                    print(txt)
                    on_map = True
                    break

            for i, building in enumerate(self.buildings):
                name = self.text_preprocess(building.name)
                if name in text:
                    txt = f"{building.name}はマップ上にあります。"
                    print(txt)
                    on_map = True
                    break

            # box内で探してみる
            for idx, item in enumerate(self.player.item_box):
                if isinstance(item, Item):
                    name = self.text_preprocess(item.name)
                    if name in text:
                        txt = f"{item.name}はボックス内にあります。"
                        print(txt)
                        in_box = True
                        break

            # 見つかりません
            if not in_box and not on_map:
                print('オブジェクトが存在しません！')
                txt = 'オブジェクトが存在しません！'
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return

        else:
            txt = "この行動を知りません。"
            print(txt)
            self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
            return

    def eval_init(self):
        """eval機能の初期化"""
        self.nlp_text = ""
        self.player.target = None
        # 戦闘か移動か
        self.player.action_type = None

    def text_preprocess(self, text):
        new_text = unicodedata.normalize("NFKC", text)  # 全角を半角へ
        new_text = text.lower()  # 英字は小文字へ
        new_text = re.sub(' ', '', new_text)  # 半角スペース削除
        new_text = re.sub('　', '', new_text)  # 全角スペース削除
        new_text = re.sub(r'[、，。,.]+', '', new_text)
        return new_text

    def use_position_with_eval(self, text, item, name_list):
        for name in name_list:
            if name in text:
                all_use_text_list = ['全部', 'すべて', '全て', 'ぜんぶ']
                # ポーションなら複数使用できる
                count = re.sub(r"\D", "", text)
                if count != "":
                    count = int(count)
                else:
                    count = 1

                for idx, obj in enumerate(self.player.item_box):
                    if type(obj) == item and isinstance(obj, Item):
                        for t in all_use_text_list:
                            if t in text:
                                count = obj.count
                        for _ in range(count):
                            self.player.use(idx)
                        txt = f"{obj.name}使用"
                        self.action_result = self.nlp_result_font.render(txt, True, Color.WHITE)
                        return True
        return False

    def buy_item_with_eval(self, text, item, name_list):
        for name in name_list:
            if name in text:
                count = re.sub(r"\D", "", text)
                if count != "":
                    count = int(count)
                else:
                    count = 1
                item_instance = item(count=count)
                self.player.buy(item_instance, self.shop)
                return True
        return False