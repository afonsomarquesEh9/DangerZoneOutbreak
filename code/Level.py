#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import sys
import pygame

from pygame import Surface, Rect
from pygame.font import Font

from code.Boss import Boss
from code.Const import (
    C_WHITE, WIN_HEIGHT, MENU_OPTION, EVENT_ENEMY, SPAWN_TIME,
    C_GREEN, C_CYAN, EVENT_TIMEOUT, TIMEOUT_STEP, TIMEOUT_LEVEL
)
from code.Enemy import Enemy
from code.Entity import Entity
from code.EntityFactory import EntityFactory
from code.EntityMediator import EntityMediator
from code.Player import Player

# class level with the constructor
class Level:
    def __init__(self, window: Surface, name: str, game_mode: str, player_score: list[int]):
        player = EntityFactory.get_entity('Player1')
        player.score = player_score[0]
        self.timeout = TIMEOUT_LEVEL
        self.window = window
        self.name = name
        self.boss_spawned = False
        self.game_mode = game_mode
        self.entity_list: list[Entity] = []
        self.entity_list.extend(EntityFactory.get_entity(self.name + 'Bg'))
        self.entity_list.append(player)
        self.boss_phase = False
        self.snd_player_shot = pygame.mixer.Sound('./asset/player_shot.wav')
        self.snd_enemy_shot = pygame.mixer.Sound('./asset/enemy_shot.wav')
        self.show_boss_warning = False
        self.warning_timer = 120

        # condition to create the player 2 entity in case of select 2 players mode cooperative or competitive
        if game_mode in [MENU_OPTION[1], MENU_OPTION[2]]:
            player = EntityFactory.get_entity('Player2')
            player.score = player_score[1]
            self.entity_list.append(player)

        pygame.time.set_timer(EVENT_ENEMY, SPAWN_TIME)
        pygame.time.set_timer(EVENT_TIMEOUT, TIMEOUT_STEP)

#---------------------------------------------------------------------------------------------------------------------#

    # update player score function
    def update_player_score(self, player_score):
        for ent in self.entity_list:
            if isinstance(ent, Player):
                if ent.name == 'Player1':
                    player_score[0] = ent.score
                elif ent.name == 'Player2':
                    player_score[1] = ent.score

#---------------------------------------------------------------------------------------------------------------------#

    # main loop responsible for updating game state, rendering and handling events
    def run(self, player_score: list[int]):
        pygame.mixer_music.load(f'./asset/{self.name}.mp3')
        pygame.mixer_music.set_volume(0.3)
        pygame.mixer_music.play(-1,0.0,10000)

        clock = pygame.time.Clock()

        while True:
            clock.tick(60)

            for ent in self.entity_list:
                self.window.blit(source=ent.surf, dest=ent.rect)
                ent.move()

                if isinstance(ent, (Player, Enemy)):
                    shoot = ent.shoot()
                    if shoot is not None:
                        self.entity_list.append(shoot)

                if ent.name == 'Player1':
                    self.level_text(
                        14,
                        f'Player1 - Health: {ent.health} | Score: {ent.score}',
                        C_GREEN,
                        (10, 25)
                    )

                if ent.name == 'Player2':
                    self.level_text(
                        14,
                        f'Player2 - Health: {ent.health} | Score: {ent.score}',
                        C_CYAN,
                        (10, 45)
                    )

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == EVENT_ENEMY and not self.boss_spawned:
                    choice = random.choice(('Enemy1', 'Enemy2'))
                    self.entity_list.append(EntityFactory.get_entity(choice))

                if event.type == EVENT_TIMEOUT:
                    self.timeout -= TIMEOUT_STEP

                    if self.timeout <= 0:

                        if self.boss_alive():
                            self.show_boss_warning = True
                            self.warning_timer = 120
                            self.timeout = 100

                        else:

                            self.update_player_score(player_score)
                            return True

                found_player = False
                for ent in self.entity_list:
                    if isinstance(ent, Player):
                        found_player = True

                if not found_player:

                    self.update_player_score(player_score)
                    self.show_game_over()
                    return False

            self.level_text(
                14,
                f'fps: {clock.get_fps():.0f}',
                C_WHITE,
                (10, WIN_HEIGHT - 35)
            )

            if self.show_boss_warning:
                self.warning_text("BOSS MUST BE DEFEATED")
                self.warning_timer -= 1

                if self.warning_timer <= 0:
                    self.show_boss_warning = False

            pygame.display.flip()

            # SPAWN BOSS
            if self.timeout <= 10000 and not self.boss_spawned:
                self.entity_list.append(EntityFactory.get_entity('Boss'))
                self.boss_spawned = True

            # COLLISIONS
            EntityMediator.verify_collision(entity_list=self.entity_list)
            EntityMediator.verify_health(entity_list=self.entity_list)

            boss_alive = False
            for ent in self.entity_list:
                if isinstance(ent, Boss):
                    boss_alive = True

            # BOSS DEFEAT
            if self.boss_spawned and not boss_alive:
                self.update_player_score(player_score)
                self.fade_out()
                self.show_level_complete()
                self.fade_in()
                return True

#---------------------------------------------------------------------------------------------------------------------#

    # fade out effect on the screen
    def fade_out(self):
        fade = pygame.Surface((self.window.get_width(), self.window.get_height()))
        fade.fill((0, 0, 0))

        for alpha in range(0, 255, 5):
            fade.set_alpha(alpha)
            self.window.blit(fade, (0, 0))
            pygame.display.flip()
            pygame.time.delay(15)

#---------------------------------------------------------------------------------------------------------------------#

    # level complete screen
    def show_level_complete(self):
        font = pygame.font.SysFont("Lucida Sans Typewriter", 40, bold=True)
        text = font.render("LEVEL COMPLETE", True, (255, 255, 255))
        rect = text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() // 2))

        self.window.fill((0, 0, 0))
        self.window.blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(2000)

#---------------------------------------------------------------------------------------------------------------------#

    # game over screen
    def show_game_over(self):
        font = pygame.font.SysFont("Lucida Sans Typewriter", 50, bold=True)
        text = font.render("YOU LOSE", True, (255, 0, 0))
        rect = text.get_rect(center=(self.window.get_width() // 2, self.window.get_height() // 2))

        pygame.mixer_music.load('./asset/Death1.wav')
        pygame.mixer_music.play()

        self.window.fill((0, 0, 0))
        self.window.blit(text, rect)
        pygame.display.flip()
        pygame.time.delay(2000)

#---------------------------------------------------------------------------------------------------------------------#

    # function created to control when the boss is alive or not
    def boss_alive(self):
        for ent in self.entity_list:
            if ent.name == 'Boss':
                return True
        return False

#---------------------------------------------------------------------------------------------------------------------#

    # warning in the low side of screen
    def warning_text(self, text):
        font = pygame.font.SysFont("Lucida Sans Typewriter", 35, bold=True)
        surf = font.render(text, True, (255, 0, 0))
        rect = surf.get_rect(center=(self.window.get_width() // 2, self.window.get_height() // 2 + 100))
        self.window.blit(surf, rect)

#---------------------------------------------------------------------------------------------------------------------#

    # function to control the type of text on the screen
    def level_text(self, text_size: int, text: str, text_color: tuple, text_pos: tuple):
        text_font: Font = pygame.font.SysFont(name="Lucida Sans Typewriter", size=text_size)
        text_surf: Surface = text_font.render(text, True, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(left=text_pos[0], top=text_pos[1])
        self.window.blit(source=text_surf, dest=text_rect)

#---------------------------------------------------------------------------------------------------------------------#

    def fade_in(self):
        pass