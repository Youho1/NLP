import pygame

class SpriteSheet:
    def __init__(self, filename):
        self.sprite_sheet = pygame.image.load(filename)

    def get_image(self, x, y, width, height):
        # 空のサーフェス
        image = pygame.Surface([width, height])
        # 透明な背景を設定
        image.set_colorkey((0, 0, 0))
        # スプライトシートから画像を切り出してコピー
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return image

    def get_all_sprites(self, width, height):
        sprites = []
        sheet_width = self.sprite_sheet.get_width()
        sheet_height = self.sprite_sheet.get_height()

        for y in range(0, sheet_height, height):
            for x in range(0, sheet_width, width):
                sprites.append(self.get_image(x, y, width, height))

        return sprites