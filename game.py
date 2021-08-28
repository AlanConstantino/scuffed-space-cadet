import pygame, sys, random, time

# helper function that calls kill method on entities passed
def kill_all(entities):
    for entity in entities:
        entity.kill()

# initialize
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Window title
pygame.display.set_caption('Scuffed Space Cadet')

# resolution
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 1080
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# sound volume
MASTER_VOLUME         = 0.5
SFX_VOLUME            = 0.5
BGM_VOLUME            = 0.8

# seconds till a new enemy spawns
SECONDS_ENEMY_SPAWN = 3
before = time.time()

# for delta time calculations
prev_time = time.time()
dt = 0

# FPS
clock = pygame.time.Clock()
FPS = 60

# assets
ENEMIES = [
    './assets/images/enemy1.png', # red enemy
    './assets/images/enemy2.png', # white enemy
    './assets/images/ship7.png',  # green enemy
]
PLAYER_IMG = './assets/images/player.png'
BULLET_IMG = './assets/images/bullet2.png'
ALIEN_IMG  = './assets/images/alien.png'      # alien boss ship

# Sound FX Path
BGM                   = './assets/sound/music/ror1-monsoon.wav'
ALIEN_HOVERING_SOUND  = './assets/sound/sfx/alien-ship-engine.ogg'
SCORE_SOUND           = './assets/sound/sfx/bonus.wav'
DEATH_SOUND           = './assets/sound/sfx/death.wav'
EXPLOSION_SOUND       = './assets/sound/sfx/explosion.ogg'
BOSS_GUN_SOUND        = './assets/sound/sfx/laserLarge_001.ogg'
PLAYER_GUN_SOUND      = './assets/sound/sfx/laserSmall2.ogg'
ENEMY_GUN_SOUND       = './assets/sound/sfx/laserSmall4.ogg'
WIN_SOUND             = './assets/sound/sfx/win.wav'

# audio channels
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

# the player is the spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, picture_path, speed = 550):
        super().__init__()
        self.prev_speed         = 0
        self.is_invincible      = False # boolean, player is either invincible or he is not
        self.last_invincible    = 0     # last time the player went invincible
        self.seconds_invincible = 2     # how long invincibility will last
        self.speed              = speed
        self.image              = pygame.transform.scale(pygame.image.load(picture_path).convert(), (50, 50)) # size of image
        self.rect               = self.image.get_rect() # size of hurtbox
        self.rect.center        = [(SCREEN_WIDTH * 0.5), (SCREEN_HEIGHT * 0.9)] # ship's spawn point
        self.lives              = 4
        self.score              = 0
        self.is_alive           = True
        self.has_won            = False
        self.has_lost           = False
        self.last_shot          = time.time()
        self.shot_delay         = 0.03
        self.damage             = 10
        self.sounds             = {
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

    def start_invincibility(self):
        self.is_invincible = True
        self.last_invincible = time.time()

    def stop_invincibility():
        self.is_invincible = False
        self.last_invincible = 0

    def update(self, dt):
        pressed_keys = pygame.key.get_pressed()
        time_to_remove_i_frames = (time.time() - self.last_invincible) >= self.seconds_invincible

        # removes player's invincibility
        if self.is_invincible and time_to_remove_i_frames:
            self.is_invincible = False
            # self.last_invincible = time.time()

        # move up
        if self.rect.top > 0:
            if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
                self.rect.y -= self.speed * dt                  # updates original y value of rect
                # self.rect.move_ip(0, -self.speed * dt)            # modifies original rect by moving it in place
                # self.rect = self.rect.move(0, -self.speed * dt) # creates a new rect and reassigns old rect to newly created rect

        # move down
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
                self.rect.y += self.speed * dt
                # self.rect.move_ip(0, self.speed * dt)
                # self.rect = self.rect.move(0, self.speed * dt)

        # move left
        if self.rect.left > 0:
            if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
                self.rect.x -= self.speed * dt
                # self.rect.move_ip(-self.speed * dt, 0)
                # self.rect = self.rect.move(-self.speed * dt, 0)

        # move right
        if self.rect.right < SCREEN_WIDTH:
            if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
                self.rect.x += self.speed * dt
                # self.rect.move_ip(self.speed * dt, 0)
                # self.rect = self.rect.move(self.speed * dt, 0)

        # shoot when space is pressed
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
    def __init__(self, picture_path, entity, speed = 800, direction = 'up', x_off = 0, y_off = 0):
        super().__init__()
        self.prev_speed  = 0
        self.speed       = speed
        self.image       = pygame.transform.scale(pygame.image.load(picture_path).convert(), (5, 20))
        self.rect        = self.image.get_rect()
        self.rect.center = [entity.rect.x + x_off, entity.rect.y + y_off]
        self.direction   = direction

    def update(self, dt):
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
        self.prev_speed  = 0
        self.speed       = random.randint(200, 450)
        self.ammo        = random.randint(1, 6)
        self.image       = pygame.transform.scale(pygame.transform.flip(pygame.image.load(picture_path).convert(), False, True), (60, 60)) # image
        self.rect        = self.image.get_rect(w = 60, h = 30) # hurtbox
        self.rect.center = [random.randint(50, SCREEN_WIDTH - 50), -10] # ship's spawn point
        self.last_shot   = time.time()
        self.shot_delay  = 0.2
        self.sounds      = {
            'shoot':   pygame.mixer.Sound(ENEMY_GUN_SOUND),
        }
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
        self.prev_speed   = 0
        self.speed        = speed
        self.ammo         = ammo
        self.image        = pygame.transform.scale(pygame.image.load(picture_path).convert(), (300, 125)) # image
        self.rect         = self.image.get_rect()     # hurtbox
        self.rect.center  = [SCREEN_WIDTH * 0.5, 150] # ship's spawn point
        self.health       = 10000
        self.is_alive     = False
        self.last_shot    = time.time()
        self.shot_delay   = 0.5
        self.sounds       = {
            'shoot':   pygame.mixer.Sound(BOSS_GUN_SOUND),
        }
        for data in self.sounds:
            self.sounds[data].set_volume(MASTER_VOLUME * SFX_VOLUME)

    def shoot(self):
        rand_fire = random.randint(5, 10)
        rand_operation = random.randint(0, 1)
        operations = ['add', 'subtract']

        for i in range(rand_fire):
            fire = 0

            if operations[rand_operation] == 'add':
                x_rand = (self.rect.width * 0.5) + random.randint(0, 100)
                y_rand = random.randint(int(self.rect.height * 0.5), self.rect.height)
                fire = Bullet(BULLET_IMG, self, random.randint(800, 1500), 'down', x_rand, y_rand)
                boss_bullet_group.add(fire)

            if operations[rand_operation] == 'subtract':
                x_rand = (self.rect.width * 0.5) - random.randint(0, 100)
                y_rand = random.randint(int(self.rect.height * 0.5), self.rect.height)
                fire = Bullet(BULLET_IMG, self, random.randint(800, 1500), 'down', x_rand, y_rand)
                boss_bullet_group.add(fire)

            ALL_SPRITES.add(fire)
        self.sounds['shoot'].play()

    def update(self, dt):
        self.rect.move_ip(self.speed * dt, 0)
        time_to_shoot = (time.time() - self.last_shot) >= self.shot_delay

        if time_to_shoot:
            self.shoot()
            self.last_shot = time.time()

        # bounce off left wall
        if self.rect.left >= 0:
            self.speed *= -1

        # bounce off right wall
        if self.rect.right <= SCREEN_WIDTH:
            self.speed *= -1

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

# to store all sprites for easy manipulation
ALL_SPRITES = pygame.sprite.Group()

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
SPAWN_BOSS_SCORE = 10000

# boss sound
boss_sound = pygame.mixer.Sound(ALIEN_HOVERING_SOUND)
channel1.play(boss_sound, -1)
channel1.pause()

# HUD
center           = (int(SCREEN_WIDTH * 0.5), int(SCREEN_HEIGHT * 0.5))
lives_HUD        = TextHUD(text = 'x{}'.format(player.lives), pos = (SCREEN_WIDTH - 20, 50))
score_HUD        = TextHUD(text = 'Score: {}'.format(0), pos = (45, 50))
boss_health_HUD  = TextHUD(text = '{:,}/10,000'.format(10000), pos = (SCREEN_WIDTH * 0.5 - 60, 50))

# game state text to be displayed on screen at a later time
win_text         = TextHUD(text = 'YOU WIN', pos = center)
game_over_text   = TextHUD(text = 'YOU DIED', pos = center,  color1 = (220, 20, 60))
paused_text      = TextHUD(text = 'PAUSED', pos = center, color1 = (255, 255, 255))

# container for player and boss hud
ALL_HUDS = []
ALL_HUDS.append(lives_HUD)
ALL_HUDS.append(score_HUD)
ALL_HUDS.append(boss_health_HUD)

# container for text screens
ALL_TEXT = []
ALL_TEXT.append(win_text)
ALL_TEXT.append(game_over_text)
ALL_TEXT.append(paused_text)

PAUSED = False

# main game loop
while True:
    clock.tick(FPS)
    SCREEN.fill((0, 0, 0)) # black

    pygame.time.delay(10)

    # delta time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    score_HUD.update(text = 'Score: {}'.format(player.score))

    ####################
    ###### CHECKS ######
    ####################

    # game over if player has no more lives
    if player.lives == 0:
        """
        Game over.
        """
        player.is_alive = False
        player.has_lost = True
        player.kill()
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

    # kill boss once health is gone
    if boss.health <= 0:
        """
        Player has won.
        """
        player.is_alive = False
        player.has_won = True
        boss.is_alive = False
        boss.is_dead = True
        boss.kill()
        kill_all(ALL_SPRITES)

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
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                """
                Pauses game.
                """
                PAUSED = not PAUSED
            if event.key == pygame.K_h:
                """
                Hides HUD when 'H' key is pressed.
                """
                for hud in ALL_HUDS:
                    hud.set_visibility(not hud.show)
            if event.key == pygame.K_r:
                """
                Restarts games when 'R' key is pressed.
                """
                spawn_regular_enemies = True

                for sprite in ALL_SPRITES:
                    sprite.kill()

                for text in ALL_TEXT:
                    text.set_visibility = False

                # reset player
                player = Spaceship(PLAYER_IMG)
                player_group.add(player)
                ALL_SPRITES.add(player)

                # reset boss
                boss = Boss(ALIEN_IMG)

                # reset HUD with new player data
                lives_HUD.update('x{}'.format(player.lives))
                score_HUD.update(text = 'Score: {}'.format(player.score))

    ##############################
    ###### ENTITY COLLISION ######
    ##############################

    # collision between a player and an enemy
    if pygame.sprite.groupcollide(player_group, enemy_group, False, True):
        """
        Player crashed into a ship.
        """
        if not player.is_invincible:
            player.score -= 100
            player.start_invincibility()
            player.lives -= 1
            player.sounds['explode']['sound'].play()
            player.sounds['explode']['has_played'] = True
            lives_HUD.update('x{}'.format(player.lives))

    # collision between an enemy's bullets and the player
    if pygame.sprite.groupcollide(player_group, enemy_bullet_group, False, True):
        """
        Player died to enemy fire.
        """
        if not player.is_invincible:
            player.score -= 100
            player.start_invincibility()
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
        new_enemy = Enemyship(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
        enemy_group.add(new_enemy)
        ALL_SPRITES.add(new_enemy)

    # collision between player and boss
    if pygame.sprite.groupcollide(player_group, boss_group, False, False):
        """
        Player collides with boss.
        """
        if not player.is_invincible:
            player.score -= 100
            player.start_invincibility()
            player.lives -= 1
            player.sounds['explode']['sound'].play()
            player.sounds['explode']['has_played'] = True
            lives_HUD.update('x{}'.format(player.lives))

    # collision between player's bullets and boss
    if pygame.sprite.groupcollide(player_bullet_group, boss_group, False, False):
        """
        Player's bullets collide with boss.
        """
        player.score += 100
        boss.health -= player.damage
        boss_health_HUD.update(text = '{:,}/10,000'.format(boss.health))

    # collision between the boss' bullets and the player
    if pygame.sprite.groupcollide(boss_bullet_group, player_group, False, False):
        """
        Boss' bullets collide with the player.
        """
        if not player.is_invincible:
            player.score -= 100
            player.start_invincibility()
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
    if player.has_won or player.has_lost:
        """
        Stop bgm, kill all sprites, stop spawning enemies/boss,
        and remove boss HUD when player wins or loses.
        """
        pygame.mixer.music.stop()
        kill_all(ALL_SPRITES)
        spawn_regular_enemies = False
        player.is_alive = False
        boss.is_alive = False
        boss_health_HUD.set_visibility(False)

    if player.has_won:
        """
        Action to take when a player wins.
        """
        win_text.draw(SCREEN)
        if not player.sounds['win']['has_played']:
            player.sounds['win']['sound'].play()
            player.sounds['win']['has_played'] = True

    if player.has_lost:
        """
        Action to take when a player loses.
        """
        game_over_text.draw(SCREEN)
        if not player.sounds['death']['has_played']:
            player.sounds['death']['sound'].play()
            player.sounds['death']['has_played'] = True

    # draw everything to screen if game is not paused, else show paused screen
    if not PAUSED:
        ALL_SPRITES.draw(SCREEN)
        ALL_SPRITES.update(dt)
    else:
        SCREEN.fill((0, 0, 0))
        paused_text.draw(SCREEN)

    # update pygame
    pygame.display.update()