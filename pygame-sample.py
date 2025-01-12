# ライブラリをインポート
import pygame
import sys

# Pygameの初期化
pygame.init()

# 画面サイズの設定
screen_dimensions = (800, 600)

# ウィンドウの作成
screen = pygame.display.set_mode(screen_dimensions)

# タイトルの設定
title = "Hello Pygame"
pygame.display.set_caption(title)

# 色の定義
white = (255, 255, 255)

# ゲームループの初期設定
clock = pygame.time.Clock()
running = True

# ゲームループ
while running:
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 画面を描画
    screen.fill(white)

    # 画面を更新
    pygame.display.flip()

    # フレームレートの設定
    clock.tick(60)

# Pygameを終了
pygame.quit()

# プログラムを終了
sys.exit()