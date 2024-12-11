# -*- coding: utf-8 -*-
# @Author  : Li Xinran
# @Comment :  1．实现了外星人生命的增加，可以在alien设置里修改参数。使得外星人被多颗子弹击中才能消灭
# 2．实现了飞船四个方向的移动
# 3. 实现了屏幕的放大与缩小。按esc切换。
# 4. 实现了最高关卡数的设置。可以通过修改setting里的参数来设置。当达到最高关卡时，
# 屏幕上会出现restart按钮，终端显示“恭喜，您已达到游戏的最高关卡！”按下restart按钮可以重新开始游戏。
# 5. 实现了一键清屏。按下c键之后，可以一键清空现有的外星人进入下一关卡。
# 6. 实现了音乐播放功能，按下”Play”按键之后可以在游戏过程中播放音乐

import sys
from socket import fromfd
from time import sleep

import pygame
from pygame.transform import scale

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from Bigbullet import BigBullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.super_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # 初始化原始屏幕尺寸变量
        self.original_screen_width = self.settings.screen_width
        self.original_screen_height = self.settings.screen_height

        # Start Alien Invasion in an inactive state.
        self.game_active = False

        # Make the Play button.
        self.play_button = Button(self, "Play")
        self.music_button = Button(self, "Play")
        self.music_button.rect.top = self.play_button.rect.bottom + 20
        self.music_button.update_position()
        self.restart_button = Button(self, "Restart")

        # 初始化缩放因子变量
        self.scale_factor_x = 1.0
        self.scale_factor_y = 1.0

        #初始化全屏标志变量
        self.fullscreen = False

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                self._check_music_button(mouse_pos)

    def _check_restart_button(self, mouse_pos):
        """Restart the game when the player clicks Restart."""
        button_clicked = self.restart_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_music_button(self, mouse_pos):
        """Play music when the player clicks Play Music."""
        button_clicked = self.music_button.rect.collidepoint(mouse_pos)
        if button_clicked:
            self.music_button.play_music()

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        #飞船的移动控制
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            #print("up up up ")
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_ESCAPE:
            # print(self.screen.get_rect())
            # self.screen = pygame.display.set_mode(
            #     (self.original_screen_width, self.original_screen_height))
            # self.ship = Ship(self)
            self._toggle_fullscreen()
        elif event.key == pygame.K_f:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.ship = Ship(self)
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_s:
            self._fire_super_bullet()
        elif event.key == pygame.K_c:  # 添加对 c 键的检测
            self._clean_screen()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _fire_super_bullet(self):
        """Create a new super bullet and add it to the super_bullets group."""
        if len(self.super_bullets) < self.settings.super_bullets_allowed :
            new_super_bullet = BigBullet(self)
            self.super_bullets.add(new_super_bullet)
            #if self.settings.super_bullets_allowed > 0:
            self.settings.super_bullets_allowed -= 1         #实现超级子弹发射数量的控制
            #print("super bullet"+str(len(self.super_bullets)))



    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        self.super_bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)


        for super_bullet in self.super_bullets.copy():
            #print("super bullet")
            if super_bullet.rect.bottom <= 0:
                self.super_bullets.remove(super_bullet)

        self._check_bullet_alien_collisions()



    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, False)
        super_collisions = pygame.sprite.groupcollide(
        self.super_bullets, self.aliens, True, False
    )

        if collisions or super_collisions:
            for aliens in collisions.values():
                for alien in aliens:
                    alien.health -= 1
                    if alien.health <= 0:
                        self.aliens.remove(alien)
                        self.stats.score += self.settings.alien_points*len(aliens)
                #self.stats.score += self.settings.alien_points * len(aliens)
            for aliens in super_collisions.values():
                for alien in aliens:
                    alien.health -= 1
                    if alien.health <= 0:
                        self.aliens.remove(alien)
                        self.stats.score += self.settings.alien_points*len(aliens)
                #self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.super_bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()


            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

             # Check if the player has reached the max level
        if self.stats.level > self.settings.max_level:
            self.game_active = False
            pygame.mouse.set_visible(True)
            self.sb.show_congratulations()
            print("恭喜，您已达到游戏的最高关卡！")
            self.restart_button.draw_button()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            # Pause.
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    # def _create_fleet(self):
    #     """Create the fleet of aliens in a single column."""
    #     alien = Alien(self)
    #     alien_width, alien_height = alien.rect.size
    #     current_x = alien_width
    #     current_y = alien_height
    #
    #     while current_y < (self.settings.screen_height - 3 * alien_height):
    #         self._create_alien(current_x, current_y)
    #         current_y += 2 * alien_height

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        # 初始化第一个外星人的位置
        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
             # 在当前行中创建外星人，直到屏幕右侧
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width

            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    # def _create_fleet(self):
    #     """Create the fleet of aliens."""
    #     # Create an alien and keep adding aliens until there's no room left.
    #     # Spacing between aliens is one alien width and one alien height.
    #     alien = Alien(self)
    #     alien_width, alien_height = alien.rect.size
    #     # 初始化第一个外星人的位置
    #     current_x, current_y = alien_width * self.scale_factor_x, alien_height * self.scale_factor_y
    #     while current_y < (self.settings.screen_height - 3 * alien_height * self.scale_factor_y):
    #        # 在当前行中创建外星人，直到屏幕右侧
    #        while current_x < (self.settings.screen_width - 2 * alien_width * self.scale_factor_x):
    #            self._create_alien(current_x, current_y)
    #            current_x += 2 * alien_width * self.scale_factor_x
    #
    #        # Finished a row; reset x value, and increment y value.
    #        current_x = alien_width * self.scale_factor_x
    #        current_y += 2 * alien_height * self.scale_factor_y

    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        for super_bullet in self.super_bullets.sprites():
            super_bullet.draw_bullet()
        self.ship.blitme()
        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.game_active:
            self.play_button.draw_button()
            if self.stats.level >3:
                self.restart_button.draw_button()
                print("restart")
            self.music_button.draw_button()
        pygame.display.flip()

    # def _toggle_fullscreen(self):
    #     alien_positions = [(alien.rect.x,alien.rect.y) for alien in self.aliens]
    #     print(f"Saved relative alien positions: {alien_positions}")
    #     # self.screen = pygame.display.set_mode(
    #     #     (self.original_screen_width, self.original_screen_height))
    #     # 清空现有的外星人舰队
    #     self.aliens.empty()
    #     for alien in self.aliens:
    #         print("x is :"+str(alien.rect.x))
    #     #if all(alien.rect.x > 800 for alien in self.aliens):
    #     for rel_x, rel_y in alien_positions:
    #         new_x = 0
    #         new_y = 0
    #         new_alien = Alien(self)
    #         new_alien.rect.x = new_x
    #         new_alien.rect.y = new_y
    #         self.aliens.add(new_alien)
    #         print(f"Added alien at position: ({new_x}, {new_y})")
    #     self.screen = pygame.display.set_mode(
    #         (self.original_screen_width, self.original_screen_height))
    #     # 重新居中飞船
    #     self.ship.center_ship()
    #
    #     # 更新屏幕
    #     self._update_screen()

    # def _toggle_fullscreen(self):
    #     # 保存外星人的相对位置
    #     alien_relative_positions = [
    #         (alien.rect.x / self.settings.screen_width, alien.rect.y / self.settings.screen_height) for alien in
    #         self.aliens]
    #     print(f"Saved relative alien positions: {alien_relative_positions}")
    #     print(f"fullscreen{self.settings.screen_height}+{self.settings.screen_width}")
    #     # 切换全屏状态
    #     #if self.fullscreen:
    #     self.screen = pygame.display.set_mode(
    #         (self.original_screen_width, self.original_screen_height))
    #     self.fullscreen = False
    #     # else:
    #     #     self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    #     #     self.fullscreen = True
    #
    #     # 更新设置中的屏幕宽度和高度
    #     self.settings.screen_width = self.screen.get_rect().width
    #     self.settings.screen_height = self.screen.get_rect().height
    #
    #     # 清空现有的外星人舰队
    #     self.aliens.empty()
    #
    #     # 根据保存的相对位置重新创建外星人
    #     for rel_x, rel_y in alien_relative_positions:
    #         x = rel_x * self.settings.screen_width
    #         y = rel_y * self.settings.screen_height
    #         new_alien = Alien(self)
    #         new_alien.rect.x = x
    #         new_alien.rect.y = y
    #         self.aliens.add(new_alien)
    #         print(f"Added alien at position: ({x}, {y})")
    #
    #     # 重新居中飞船
    #     self.ship.center_ship()
    #
    #     # 更新屏幕
    #     self._update_screen()

    # def _toggle_fullscreen(self):
    #
    #     if self.fullscreen:
    #        # 恢复原来的窗口模式
    #        self.screen = pygame.display.set_mode(
    #            (self.original_screen_width, self.original_screen_height))
    #        self.scale_factor_x = 1
    #        self.scale_factor_y = 1
    #     else:
    #        # 进入全屏模式
    #        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    #        self.settings.screen_width = self.screen.get_width()
    #        self.settings.screen_height = self.screen.get_height()
    #        self.scale_factor_x = self.settings.screen_width / self.original_screen_width
    #        self.scale_factor_y = self.settings.screen_height / self.original_screen_height
    #
    #     # 调整飞船的位置和大小
    #     self.ship.rect.x = int(self.ship.rect.x * self.scale_factor_x)
    #     self.ship.rect.y = int(self.ship.rect.y * self.scale_factor_y)
    #     self.ship.image = pygame.transform.scale(self.ship.image, (int(self.ship.rect.width * self.scale_factor_x), int(self.ship.rect.height * self.scale_factor_y)))
    #
    #     # 调整子弹的位置和大小
    #     for bullet in self.bullets:
    #        bullet.rect.x = int(bullet.rect.x * self.scale_factor_x)
    #        bullet.rect.y = int(bullet.rect.y * self.scale_factor_y)
    #        bullet.image = pygame.transform.scale(bullet.image, (int(bullet.rect.width * self.scale_factor_x), int(bullet.rect.height * self.scale_factor_y)))
    #
    #     # 调整超级子弹的位置和大小
    #     for super_bullet in self.super_bullets:
    #        super_bullet.rect.x = int(super_bullet.rect.x * self.scale_factor_x)
    #        super_bullet.rect.y = int(super_bullet.rect.y * self.scale_factor_y)
    #        super_bullet.image = pygame.transform.scale(super_bullet.image, (int(super_bullet.rect.width * self.scale_factor_x), int(super_bullet.rect.height * self.scale_factor_y)))
    #
    #     # 清空现有的外星人舰队
    #     self.aliens.empty()
    #
    #     self.fullscreen = not self.fullscreen
    #     self.ship.center_ship()  # 重新居中飞船
    #     self._create_fleet()  # 重新创建外星人舰队
    #     self._update_screen()
    #     self.sb.update_positions()
    #     self.play_button.update_position()
    #     self.music_button.update_position()
    #     print("屏幕尺寸为" + str(self.settings.screen_height) + " " + str(self.settings.screen_width))

    # def _toggle_fullscreen(self):
    #
    #
    #     # 保存外星人的相对位置
    #     alien_relative_positions = [
    #         (alien.rect.x / self.settings.screen_width, alien.rect.y / self.settings.screen_height) for alien in
    #         self.aliens]
    #     print(f"Saved relative alien positions: {alien_relative_positions}")
    #
    #     # 切换全屏状态
    #     if self.fullscreen:
    #         self.screen = pygame.display.set_mode(
    #             (self.original_screen_width, self.original_screen_height))
    #         self.fullscreen = False
    #     else:
    #         self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    #         self.fullscreen = True
    #
    #     # 更新设置中的屏幕宽度和高度
    #     self.settings.screen_width = self.screen.get_rect().width
    #     self.settings.screen_height = self.screen.get_rect().height
    #
    #     # 清空现有的外星人舰队
    #     self.aliens.empty()
    #     self.scale_factor= self.settings.screen_width / self.original_screen_width
    #     # 根据保存的相对位置重新创建外星人
    #     for rel_x, rel_y in alien_relative_positions:
    #         x = rel_x * self.settings.screen_width
    #         y = rel_y * self.settings.screen_height
    #         new_alien = Alien(self, scale_factor=self.scale_factor)  # 使用缩放因子
    #         new_alien.rect.x = x
    #         new_alien.rect.y = y
    #         self.aliens.add(new_alien)
    #         print(f"Added alien at position: ({x}, {y})")
    #
    #     # 重新居中飞船
    #     self.ship.center_ship()
    #
    #     # 更新屏幕
    #     self._update_screen()

    def _toggle_fullscreen(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((self.original_screen_width, self.original_screen_height))
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.fullscreen = not self.fullscreen

    def _clean_screen(self):
        # 记录被清除的外星人数
        num_aliens_cleared = len(self.aliens)
        self.aliens.empty()  # 清空所有外星人
        self._update_screen()  # 更新屏幕以反映变化
        #self.screen.fill(self.settings.bg_color)  # 使用背景颜色清屏
        sleep(0.5)
        print("Cleared " + str(num_aliens_cleared) + " aliens.")
        # 更新得分
        self.stats.score += self.settings.alien_points * num_aliens_cleared
        print("Current score: " + str(self.stats.score))
        print('points:'+str(self.settings.alien_points))
        self.sb.prep_score()  # 更新得分板
        self.sb.check_high_score()  # 检查是否为最高分


        self._update_screen()  # 更新屏幕以反映变化





if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()