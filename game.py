########## GAMEPLAY ELEMENTS ##############
# TODO
# - Give the player some invincibility frames after taking damage/dying
# - Add a game over screen
# - Add a win screen
# - Add a restart button after the win screen
# - Stagger the bullets when firing for all entities (they spawn too fast)
# - Add pause functionality to game
# - Add a simple menu (play, exit, options... if it isn't a pain in the ass)

# BUGS:
# - Boss shooting not working properly
# - When reaching Game Over screen, it still spawns enemies,
#   doesn't happen when you reach Win screen though
# - When hit by a boss bullet, you instantly die instead of
#   subtracting a life, you just lost. Has something to do
#   with the shoot() method in Boss class

import pygame, sys, random, time

before = time.time()

# initialize
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Window title
pygame.display.set_caption('Scuffed Space Cadet')

# FPS
clock = pygame.time.Clock()
FPS = 60

# for delta time calculations
prev_time = time.time()
dt = 0

# resolution
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1080
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# assets
ENEMIES = [
    './assets/images/enemy1.png', # red enemy
    './assets/images/enemy2.png', # white enemy
    './assets/images/ship7.png',  # green enemy
]
# PLAYER_IMG = './assets/images/ship5.png'
PLAYER_IMG = './assets/images/player.png'
BULLET_IMG = './assets/images/bullet2.png'
BOSS_IMG   = './assets/images/evil-ship.png'  # purple boss ship
ALIEN_IMG  = './assets/images/alien.png'      # alien boss ship

# sound volume
MASTER_VOLUME         = 0.5
SFX_VOLUME            = 0.5
BGM_VOLUME            = 0.8

# Sound FX Path
PLAYER_GUN_SOUND      = './assets/sound/sfx/laserSmall2.ogg'
ENEMY_GUN_SOUND       = './assets/sound/sfx/laserSmall4.ogg'
BOSS_GUN_SOUND        = './assets/sound/sfx/laserSmall3.ogg'
EXPLOSION_SOUND       = './assets/sound/sfx/explosion.ogg'
SCORE_SOUND           = './assets/sound/sfx/bonus.wav'
DEATH_SOUND           = './assets/sound/sfx/death.wav'
WIN_SOUND             = './assets/sound/sfx/win.wav'
ALIEN_HOVERING_SOUND  = './assets/sound/sfx/alien-ship-engine.ogg'
BGM                   = './assets/sound/music/ror1-monsoon.wav'

# audio channels
# channels_reserved = 3
# for i in range(channels_reserved):
#     pygame.mixer.set_reserved(i)
pygame.mixer.set_reserved(1)
channel1 = pygame.mixer.Channel(0) # boss ship engine sound
channel2 = pygame.mixer.Channel(1) # unused
channel3 = pygame.mixer.Channel(2) # unused
channel4 = pygame.mixer.Channel(3) # unused
channel5 = pygame.mixer.Channel(4) # unused
channel6 = pygame.mixer.Channel(5) # unused
channel7 = pygame.mixer.Channel(6) # unused
channel8 = pygame.mixer.Channel(7) # unused

# BGM music
pygame.mixer.music.load(BGM)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(MASTER_VOLUME * BGM_VOLUME)

# to store all sprites for easy manipulation
ALL_SPRITES = pygame.sprite.Group()

# the player is the spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, picture_path, speed = 550):
        super().__init__()
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (50, 50)) # size of image
        self.rect = self.image.get_rect() # size of hurtbox
        self.rect.center = [(SCREEN_WIDTH * 0.5), (SCREEN_HEIGHT * 0.9)] # ship's spawn point
        self.lives = 3
        self.score = 0
        self.is_alive = True
        self.has_won = False
        self.has_lost = False
        self.last_shot = time.time()
        self.shot_delay = 0.03
        self.damage = 10
        self.sounds = {
            'explode': {
                'has_played': False,
                'sound': pygame.mixer.Sound(EXPLOSION_SOUND),
            },
            'shoot':   {
                'has_played': False,
                'sound': pygame.mixer.Sound(PLAYER_GUN_SOUND),
            },
            'score':   {
                'has_played': False,
                'sound': pygame.mixer.Sound(SCORE_SOUND)
            },
            'death':   {
                'has_played': False,
                'sound': pygame.mixer.Sound(DEATH_SOUND),
            },
            'win':     {
                'has_played': False,
                'sound': pygame.mixer.Sound(WIN_SOUND),
            },
        }
        # setting volume level for sounds
        for data in self.sounds:
            self.sounds[data]['sound'].set_volume(MASTER_VOLUME * SFX_VOLUME)

    def shoot(self):
        bullet = Bullet(BULLET_IMG, self, 1800, 'up', (self.rect.width * 0.5), 0) # what the bullet looks like
        ALL_SPRITES.add(bullet)     # adding bullet to ALL_SPRITES group
        player_bullet_group.add(bullet)    # added bullet to bullet group

    def update(self, dt):
        if self.speed <= 0:
            return
        else:
            pressed_keys = pygame.key.get_pressed()

            # move up
            if self.rect.top > 0:
                if pressed_keys[pygame.K_UP]:
                    self.rect.move_ip(0, -self.speed * dt) # modifies original rect by moving it in place
                    # self.rect.y -= self.speed * dt # updates original y value of rect
                    # self.rect = self.rect.move(0, -self.speed * dt) # creates a new rect and reassigns old rect to newly created rect

            # move down
            if self.rect.bottom < SCREEN_HEIGHT:
                if pressed_keys[pygame.K_DOWN]:
                    self.rect.move_ip(0, self.speed * dt)
                    # self.rect.y += self.speed * dt
                    # self.rect = self.rect.move(0, self.speed * dt)

            # move left
            if self.rect.left > 0:
                if pressed_keys[pygame.K_LEFT]:
                    self.rect.move_ip(-self.speed * dt, 0)
                    # self.rect.x -= self.speed * dt
                    # self.rect = self.rect.move(-self.speed * dt, 0)

            # move right
            if self.rect.right < SCREEN_WIDTH:
                if pressed_keys[pygame.K_RIGHT]:
                    self.rect.move_ip(self.speed * dt, 0)
                    # self.rect.x += self.speed * dt
                    # self.rect = self.rect.move(self.speed * dt, 0)

            if pressed_keys[pygame.K_SPACE]:
                now = time.time()
                time_to_shoot = (now - self.last_shot) >= self.shot_delay
                if time_to_shoot:
                    channel1.play(self.sounds['shoot']['sound'], 0)
                    self.sounds['shoot']['has_played'] = True
                    self.shoot()
                    self.last_shot = now

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    # picture_path - string - a path to an image
    # entity       - Class  - the instance of the class that will shoot bullets
    # offset       - number - the offset to shoot bullets in the middle of entity
    # direction    - string - the direction in which the bullet is going (i.e. left, right, up, down)
    # x_off        - number - offset of x coordinate
    # y_off        - number - offset of y coordinate
    def __init__(self, picture_path, entity, speed = 800, direction = 'up', x_off = 0, y_off = 0):
        super().__init__()
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (5, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [entity.rect.x + x_off, entity.rect.y + y_off]
        self.direction = direction

    def update(self, dt):
        if self.speed <= 0:
            return
        else:
            # shoot bullet upwards
            if self.direction == 'up':
                self.rect.move_ip(0, -self.speed * dt)

            # shoot bullet downwards
            if self.direction == 'down':
                self.rect.move_ip(0, self.speed * dt)

            # remove bullet if top of screen is reached
            # player can only shoot upward
            if self.rect.y < 0:
                self.kill()

            # remove bullet if bottom of screen is reached
            # enemies can only shoot downward
            if self.rect.y > SCREEN_HEIGHT:
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Enemyship(pygame.sprite.Sprite):
    def __init__(self, picture_path):
        super().__init__()
        self.speed = random.randint(200, 450)
        self.ammo = random.randint(1, 5)
        self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load(picture_path).convert(), False, True), (60, 60)) # image
        self.rect = self.image.get_rect(w = 60, h = 30) # hurtbox
        self.rect.center = [random.randint(50, SCREEN_WIDTH - 50), -10] # ship's spawn point
        self.last_shot = time.time()
        self.shot_delay = 0.2
        self.sounds = {
            'shoot':   pygame.mixer.Sound(ENEMY_GUN_SOUND),
        }
        # setting volume level for sounds
        for data in self.sounds:
            self.sounds[data].set_volume(MASTER_VOLUME * SFX_VOLUME)

    def shoot(self):
        now = time.time()
        time_to_shoot = (now - self.last_shot) >= self.shot_delay
        if time_to_shoot:
            self.sounds['shoot'].play()
            new_bullet = Bullet(BULLET_IMG, self, 600, 'down', (self.rect.width * 0.5), (self.rect.height * 0.5) + 50)
            enemy_bullet_group.add(new_bullet)
            ALL_SPRITES.add(new_bullet)
            self.ammo -= 1
            self.last_shot = time.time()

    def update(self, dt):
        if self.speed <= 0:
            return
        else:
            self.rect.move_ip(0, self.speed * dt)

            if self.ammo > 0:
                self.shoot()

            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
                self.rect.y = 0
                self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Boss(pygame.sprite.Sprite):
    def __init__(self, picture_path, speed = 300, ammo = random.randint(10, 20)):
        super().__init__()
        self.speed = speed
        self.ammo = ammo
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (300, 125)) # image
        self.rect = self.image.get_rect(w = 300, h = 100) # hurtbox
        self.rect.center = [random.randint(200, SCREEN_WIDTH - 300), 150] # ship's spawn point
        self.health = 10000     # total boss health
        # self.health = 1
        self.is_alive = False
        self.last_reload = time.time()
        self.reload_delay = 1
        self.last_shot = time.time()
        self.shot_delay = 0.05
        self.sounds = {
            'shoot':   pygame.mixer.Sound(BOSS_GUN_SOUND),
        }
        # setting volume level for sounds
        for data in self.sounds:
            self.sounds[data].set_volume(MASTER_VOLUME * SFX_VOLUME)

    def reload(self):
        time_to_reload = (now - self.last_reload) >= self.reload_delay
        if time_to_reload:
            self.ammo = random.randint(10, 20)

    def shoot(self):
        now = time.time()
        time_to_shoot = (now - self.last_shot) >= self.shot_delay
        if time_to_shoot:
            bullet_speed = 600
            self.sounds['shoot'].play()
            left_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', 0, self.rect.bottom)
            middle_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', (self.rect.width * 0.5), self.rect.bottom)
            right_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.width, self.rect.bottom)
            boss_bullet_group.add(left_fire, middle_fire, right_fire)
            ALL_SPRITES.add(left_fire, middle_fire, right_fire)
            self.ammo -= 1
            self.last_shot = now

    def update(self, dt):
        self.rect.move_ip(self.speed * dt, 0)
        now = time.time()

        # shoot all ammo
        if self.ammo >= 0:
            self.shoot()
        else:
            self.reload()

        if self.ammo <= 0 and (now - self.last_reload) >= self.reload_delay:
            self.last_reload = now
            self.reload()

        # bounce off left wall
        if self.rect.left >= 0:
            self.speed *= -1

        # bounce off right wall
        if self.rect.right <= SCREEN_WIDTH:
            self.speed *= -1

        if self.rect.bottom >= SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = 0
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Class wrapper for writing Text HUDs
class TextHUD:
    def __init__(self,  size = 32, text = '', font = 'freesansbold.ttf', pos = (0, 0), color1 = (255, 255, 255), color2 = None):
        self.size = size
        self.font = pygame.font.Font(font, size)
        self.text = self.font.render(str(text), True, color1, color2)
        self.pos  = (abs(pos[0] - size), abs(pos[1] - size))
        self.show = True

    def set_visibility(self, visibility):
        self.show = visibility

    def update(self, text, anti_alias = True, color1 = (255, 255, 255), color2 = None):
        if self.show == True:
            self.text = self.font.render('{}'.format(str(text)), True, color1, color2)

    def draw(self, surface):
        if self.show == True:
            surface.blit(self.text, self.pos)

def kill_all(entities):
    for entity in entities:
        entity.kill()

SECONDS_ENEMY_SPAWN = 3 # seconds till a new enemy spawns

# Groups
player_group        = pygame.sprite.GroupSingle() # player
boss_group          = pygame.sprite.GroupSingle() # boss
enemy_group         = pygame.sprite.Group()       # enemies
player_bullet_group = pygame.sprite.Group()       # player bullets
boss_bullet_group   = pygame.sprite.Group()       # boss bullets
enemy_bullet_group  = pygame.sprite.Group()       # enemy bullets

# Player
player = Spaceship(PLAYER_IMG)
player_group.add(player)
ALL_SPRITES.add(player)

# Alien Boss
boss = Boss(ALIEN_IMG)
spawn_regular_enemies = True
SPAWN_BOSS_SCORE = 1000
# SPAWN_BOSS_SCORE = 10

# boss sound
boss_sound = pygame.mixer.Sound(ALIEN_HOVERING_SOUND)
channel1.play(boss_sound, -1)
channel1.pause()

# HUD
center          = (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5)
lives_HUD       = TextHUD(text = 'x{}'.format(player.lives), pos = (SCREEN_WIDTH - 20, 50))
score_HUD       = TextHUD(text = 'Score: {}'.format(0), pos = (45, 50))
boss_health_HUD = TextHUD(text = '{:,}/10,000'.format(10000), pos = (SCREEN_WIDTH * 0.5 - 60, 50))

# game state text to be displayed on screen at a later time
win_text         = TextHUD(text = 'You Win', pos = center)
game_over_text   = TextHUD(text = 'YOU DIED', pos = center,  color1 = (220, 20, 60))
paused_text      = TextHUD(text = 'Paused', pos = center, color1 = (255, 255, 255))

ALL_HUDS = []
ALL_HUDS.append(lives_HUD)
ALL_HUDS.append(score_HUD)
ALL_HUDS.append(boss_health_HUD)

GAME_STATE = {
    'paused': False,
}

# def loop(ALL_SPRITES):
#     while GAME_STATE['paused']:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             if event.type == pygame.KEYUP:
#                 if event.key == pygame.K_ESCAPE:
#                     GAME_STATE['paused'] = not GAME_STATE['paused']
#                     for sprite in ALL_SPRITES:
#                         sprite.stop()
#         SCREEN.fill((20, 20, 20))
#         paused_text.draw(SCREEN)
#         pygame.display.update()
#     for sprite in ALL_SPRITES:
#         sprite.start()

# main game loop
while True:
    clock.tick(FPS)
    SCREEN.fill((0, 0, 0)) # black

    pygame.time.delay(10)

    # delta time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    ####################
    ###### CHECKS ######
    ####################

    # game over if player has no more lives
    if player.lives == 0:
        """
        Game over.
        """
        print('GAME OVER!')
        player.is_alive = False
        player.has_lost = True
        player.kill()
        kill_all(ALL_SPRITES)

    # kill boss once health is gone
    if boss.health <= 0:
        """
        Player has won.
        """
        print('YOU WIN!')
        player.is_alive = False
        player.has_won = True
        boss.is_alive = False
        boss.is_dead = True
        boss.kill()
        kill_all(ALL_SPRITES)

    # remove enemies and spawn boss if score threshold is reached
    if player.score >= SPAWN_BOSS_SCORE:
        """
        Remove all enemies and spawn boss if score threshold is reached.
        """
        kill_all(enemy_group)

        if boss.is_alive == False:
            boss.is_alive = True
            spawn_regular_enemies = False
            boss_group.add(boss)
            ALL_SPRITES.add(boss)

    # every 3 seconds, spawn a new enemy
    if spawn_regular_enemies and now - before > SECONDS_ENEMY_SPAWN:
        """
        Enemy spawn rate.
        """
        before = now
        new_enemy = Enemyship(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
        enemy_group.add(new_enemy)
        ALL_SPRITES.add(new_enemy)

    #########################
    ###### GAME EVENTS ######
    #########################

    # check for events
    for event in pygame.event.get():
        """
        Event checking/handling.
        """
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_h:
                # turns off all HUD
                for hud in ALL_HUDS:
                    hud.set_visibility(not hud.show)

    ##############################
    ###### ENTITY COLLISION ######
    ##############################

    # collision between a player and an enemy
    if pygame.sprite.groupcollide(player_group, enemy_group, False, True):
        """
        Player crashed into a ship.
        """
        player.lives -= 1
        player.sounds['explode']['sound'].play()
        player.sounds['explode']['has_played'] = True
        lives_HUD.update('x{}'.format(player.lives))

    # collision between an enemy's bullets and the player
    if pygame.sprite.groupcollide(player_group, enemy_bullet_group, False, True):
        """
        Player died to enemy fire.
        """
        player.lives -= 1
        player.sounds['explode']['sound'].play()
        player.sounds['explode']['has_played'] = True
        lives_HUD.update('x{}'.format(player.lives))

    # collision between player's bullets and enemies
    if pygame.sprite.groupcollide(player_bullet_group, enemy_group, True, True):
        """
        Player killed an enemy. Spawns a new enemy whenever the player kills an enemy.
        """
        player.score += 100
        player.sounds['score']['sound'].play()
        player.sounds['score']['has_played'] = True
        score_HUD.update(text = 'Score: {}'.format(player.score))
        new_enemy = Enemyship(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
        enemy_group.add(new_enemy)
        ALL_SPRITES.add(new_enemy)

    # collision between player and boss
    if pygame.sprite.groupcollide(player_group, boss_group, False, False):
        """
        Player collides with boss.
        """
        player.lives -= 1
        player.sounds['explode']['sound'].play()
        player.sounds['explode']['has_played'] = True
        lives_HUD.update('x{}'.format(player.lives))

    # collision between player's bullets and boss
    if pygame.sprite.groupcollide(player_bullet_group, boss_group, False, False):
        """
        Player's bullets collide with boss.
        """
        boss.health -= player.damage
        boss_health_HUD.update(text = '{:,}/10,000'.format(boss.health))

    # collision between the boss' bullets and the player
    if pygame.sprite.groupcollide(boss_bullet_group, player_group, False, False):
        """
        Boss' bullets collide with the player.
        """
        player.lives -= 1
        player.sounds['explode']['sound'].play()
        player.sounds['explode']['has_played'] = True
        lives_HUD.update('x{}'.format(player.lives))

    #########################
    ###### GAME STATUS ######
    #########################

    # show player hud as long as they are alive
    if player.is_alive:
        """
        As long as the player is still alive, show the player's HUD.
        """
        lives_HUD.draw(SCREEN)
        score_HUD.draw(SCREEN)

    # show enemy hud as long as they are alive
    if boss.is_alive:
        """
        As long as the boss is still alive, show it's health HUD.
        """
        boss_health_HUD.draw(SCREEN)

    # draw win screen if player won
    if player.has_won:
        """
        Action to take when a player wins.
        """
        pygame.mixer.music.stop()
        spawn_regular_enemies = False
        boss.is_alive = False
        player.is_alive = False
        boss_health_HUD.set_visibility(False)
        kill_all(ALL_SPRITES)

        # if sound has not played yet, play it
        if not player.sounds['win']['has_played']:
            player.sounds['win']['sound'].play()
            player.sounds['win']['has_played'] = True

        win_text.draw(SCREEN)

    # draw lose screen if player lost
    if player.has_lost:
        """
        Action to take when the player has lost.
        """
        pygame.mixer.music.stop()
        spawn_regular_enemies = False
        boss.is_alive = False
        player.is_alive = False
        boss_health_HUD.set_visibility(False)
        kill_all(ALL_SPRITES)

        # if sound has not played yet, play it
        if not player.sounds['death']['has_played']:
            player.sounds['death']['sound'].play()
            player.sounds['death']['has_played'] = True

        game_over_text.draw(SCREEN)

    # draws all sprites to screen
    ALL_SPRITES.draw(SCREEN)

    # updates the position of all sprites (i.e. moving surfaces)
    ALL_SPRITES.update(dt)

    # update pygame
    pygame.display.update()