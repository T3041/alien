import pygame.sprite


class BigBullet(pygame.sprite.Sprite):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.super_bullet_color
        #self.count = 0

        #self.image = pygame.sprite.SizedSprite(self.screen, (self.settings.s_bullet_width, self.settings.s_bullet_height))

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.super_bullet_width,
            self.settings.super_bullet_height)
        # 将当前矩形对象的中心设为飞船的中心
        self.rect.midtop = ai_game.ship.rect.midtop
        # 将当前矩形对象的中心设为屏幕的中心
        #self.rect"""Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.super_bullet_color
        self.screen_rect = ai_game.screen.get_rect()

        #self.count = 0

        #self.image = pygame.sprite.SizedSprite(self.screen, (self.settings.s_bullet_width, self.settings.s_bullet_height))

        # Create a bullet rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.screen_rect.width,
            self.settings.super_bullet_height)
        # 将当前矩形对象的中心设为飞船的中心
        self.rect.midbottom = ai_game.ship.rect.midtop
        #self.rect.bottomright= self.screen_rect.bottomright
        # 将当前矩形对象的中心设为屏幕的中心
        #self.rect.center = ai_game.screen.get_rect().center
        #self.rect.bottom = ai_game.screen.get_rect().bottom-30

        self.rect.y = ai_game.ship.rect.y
        self.rect.x = 0
        # Store the bullet's position as a float.
        self.y = float(self.rect.y)
        self.x = 0

    def update(self):
        """Move the bullet up the screen."""
        # Update the exact position of the bullet.
        self.y -= self.settings.super_bullet_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)