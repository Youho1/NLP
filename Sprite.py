import os
import pygame

class Sprite(pygame.sprite.Sprite):
    def __init__(self, image_path, x, y, size):
        super().__init__()
        #print('画像を作る')
        self.load_and_scale_image(image_path, size)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_and_scale_image(self, image_path, size):
        try:
            # 画像が存在するか確認
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"画像ファイルが見つかりません: {image_path}")

            # 画像の読み込みと最適化
            original_image = pygame.image.load(image_path).convert_alpha()

            # 画像のリサイズ
            self.image = pygame.transform.scale(original_image, size)
        except (pygame.error, FileNotFoundError) as e:
            print(f"画像の読み込みエラー: {e}")
            # エラー時はデフォルトの四角形を表示
            self.image = pygame.Surface(size)
            self.image.fill((255, 0, 0))  # 赤色

    def resize(self, new_size):
        """画像を新しいサイズにリサイズするメソッド"""
        self.image = pygame.transform.scale(self.image, new_size)
        original_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = original_center

    def change_position(self, position):
        self.rect.x = position[0]
        self.rect.y = position[1]
