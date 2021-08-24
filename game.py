########## GAMEPLAY ELEMENTS ##############
# TODO
# - Give the player some invincibility frames after taking damage/dying
# - Add a game over screen
# - Add a win screen
# - Add a restart button after the win screen
# - Stagger the bullets when firing for all entities (they spawn too fast)
# - Add pause functionality to game
# - Add a simple menu (play, exit, options... if it isn't a pain in the ass)
# - Add funny sound effects
# - Use Dark Souls moan sound whenever your life gets taken away
# - Use Dark Souls death sound whenever you die
# - Use Dark Souls "Very good" fx when player wins
# - Use Tyler1 gun sound fx for bullet shooting

import pygame, sys, random, time

before = time.time()

# initialize
pygame.init()
pygame.font.init()

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
# GUNSHOT_SOUND = './assets/sound/gunshot.wav'  # gunshot sound

# to store all sprites for easy manipulation
ALL_SPRITES = pygame.sprite.Group()

# state
PAUSED = False

# the player is the spaceship
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, picture_path, speed = 550):
        super().__init__()
        self.prev_speed = 0
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (50, 50)) # size of image
        self.rect = self.image.get_rect() # size of hurtbox
        self.rect.center = [(SCREEN_WIDTH * 0.5), (SCREEN_HEIGHT * 0.9)] # ship's spawn point
        self.lives = 3
        self.score = 0
        self.has_won = False
        self.has_lost = False
        self.last_shot = time.time()
        self.shot_delay = 0.0125

    def stop(self):
        self.prev_speed = self.speed
        self.speed = 0

    def move(self, speed = None):
        if speed is None:
            self.speed = self.prev_speed if self.prev_speed != 0 else 550
        else:
            self.speed = speed if speed != 0 else 550

    def shoot(self):
        # self.firing_sound.play()
        bullet = Bullet(BULLET_IMG, self, 1800, 'up', (self.rect.width * 0.5), 0) # what the bullet looks like
        ALL_SPRITES.add(bullet)     # adding bullet to ALL_SPRITES group
        player_bullet_group.add(bullet)    # added bullet to bullet group

    def update(self, dt):
        pressed_keys = pygame.key.get_pressed()

        # move up
        if self.rect.top > -10:
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
        if self.rect.left > -20:
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
        self.prev_speed = 0
        self.speed = speed
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (5, 20))
        self.rect = self.image.get_rect()
        self.rect.center = [entity.rect.x + x_off, entity.rect.y + y_off] # add 50px for offset since ship width is 100px
        self.direction = direction

    def stop(self):
        self.prev_speed = self.speed
        self.speed = 0

    def move(self, speed = None):
        if speed is None:
            self.speed = self.prev_speed if self.prev_speed != 0 else 800
        else:
            self.speed = speed if speed != 0 else 800

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
        self.prev_speed = 0
        self.speed = random.randint(200, 450)
        self.ammo = random.randint(1, 5)
        self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load(picture_path).convert(), False, True), (60, 60)) # image
        self.rect = self.image.get_rect(w = 60, h = 30) # hurtbox
        self.rect.center = [random.randint(50, SCREEN_WIDTH - 50), -10] # ship's spawn point
        self.last_shot = time.time()
        self.shot_delay = 0.1

    def stop(self):
        self.prev_speed = self.speed
        self.speed = 0

    def move(self, speed = None):
        if speed is None:
            self.speed = self.prev_speed if self.prev_speed != 0 else random.randint(200, 450)
        else:
            self.speed = speed if speed != 0 else random.randint(200, 450)

    def shoot(self):
        now = time.time()
        time_to_shoot = (now - self.last_shot) >= self.shot_delay
        if time_to_shoot:
            new_bullet = Bullet(BULLET_IMG, self, 600, 'down', (self.rect.width * 0.5), (self.rect.height * 0.5) + 50)
            enemy_bullet_group.add(new_bullet)
            ALL_SPRITES.add(new_bullet)
            self.ammo -= 1
            self.last_shot = now

    def update(self, dt):
        self.rect.move_ip(0, self.speed * dt)

        if self.ammo >= 0:
            self.shoot()

        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - 50)
            self.rect.y = 0
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Boss(pygame.sprite.Sprite):
    def __init__(self, picture_path, speed = 300, ammo = random.randint(10, 25)):
        super().__init__()
        self.prev_speed = 0
        self.speed = speed
        self.ammo = ammo
        self.image = pygame.transform.scale(pygame.image.load(picture_path).convert(), (300, 125)) # image
        self.rect = self.image.get_rect(w = 300, h = 100) # hurtbox
        self.rect.center = [random.randint(200, SCREEN_WIDTH - 300), 150] # ship's spawn point
        # self.last = time.time() # last time you emptied your ammo
        self.cooldown = 1       # seconds to wait after reload
        self.health = 10000     # total boss health
        # self.health = 1
        self.is_alive = True
        self.last_shot = time.time()
        self.shot_delay = 1

    def stop(self):
        self.prev_speed = self.speed
        self.speed = 0

    def move(self, speed = None):
        if speed is None:
            self.speed = self.prev_speed if self.prev_speed != 0 else 300
        else:
            self.speed = speed if speed != 0 else 300
        # elif speed >= 0:
            # self.speed = 300

    def reload(self):
        self.ammo = random.randint(10, 30)
        # self.ammo = 30

    def shoot(self):
        now = time.time()
        time_to_shoot = (now - self.last_shot) >= self.shot_delay
        if time_to_shoot:
            # bullet_speed = random.randint(400, 500)
            bullet_speed = 700
            # print(self.rect.x)
            # print(self.rect.y)

            # as boss ship slides to right, it has a bigger spread than going left
            # left_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left * 0.2, self.rect.bottom)
            # middle_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left * 0.5, self.rect.bottom)
            # right_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left * 0.8, self.rect.bottom)

            left_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.width * 0.5, self.rect.bottom)
            boss_bullet_group.add(left_fire)
            ALL_SPRITES.add(left_fire)
            # left_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left + 20, self.rect.bottom)
            # middle_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left + 60, self.rect.bottom)
            # right_fire = Bullet(BULLET_IMG, self, bullet_speed, 'down', self.rect.left + 100, self.rect.bottom)

            # boss_bullet_group.add(left_fire, middle_fire, right_fire)
            # ALL_SPRITES.add(left_fire, middle_fire, right_fire)
            if self.ammo <= 0:
                self.reload()
            else:
                self.ammo -= 1
            self.last_shot = time.time()

    def update(self, dt):
        self.rect.move_ip(self.speed * dt, 0)
        # now = time.time()

        if self.ammo >= 0:
            self.shoot()

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

    def update(self, text, anti_alias = True, color1 = (255, 255, 255), color2 = None):
        self.text = self.font.render('{}'.format(str(text)), True, color1, color2)

    def draw(self, surface):
        surface.blit(self.text, self.pos)

PAUSED = False

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
spawned_boss = False
spawn_regular_enemies = True
SPAWN_BOSS_SCORE = 10

# HUD
center           = (SCREEN_WIDTH * 0.5, SCREEN_HEIGHT * 0.5)
SHOW_PLAYER_HUD  = True
lives_HUD        = TextHUD(text = 'x{}'.format(player.lives), pos = (SCREEN_WIDTH - 20, 50))
score_HUD        = TextHUD(text = 'Score: {}'.format(0), pos = (45, 50))
boss_health_HUD  = TextHUD(text = '{:,}/10,000'.format(10000), pos = (SCREEN_WIDTH * 0.5 - 60, 50))
win_HUD          = TextHUD(text = 'You Win', pos = center)
game_over_HUD    = TextHUD(text = 'Game Over', pos = center)
paused_HUD       = TextHUD(text = 'Paused', pos = center, color1 = (0,0,0))

# main game loop
while True:
    clock.tick(FPS)
    SCREEN.fill((0, 0, 0)) # black

    # delta time
    now = time.time()
    dt = now - prev_time
    prev_time = now

    # game over if player has no more lives
    if player.lives == 0:
        """
        Game over.
        """
        print('GAME OVER!')
        player.has_lost = True
        player.kill()
        for sprite in ALL_SPRITES:
            sprite.kill()
        # pygame.quit()
        # sys.exit()

    if boss.health <= 0:
        """
        Player has won.
        """
        print('YOU WIN!')
        boss.is_alive = False
        boss.kill()
        player.has_won = True
        for sprite in ALL_SPRITES:
            sprite.kill()

        # SCREEN.fill((255, 255, 255))
        # pygame.quit()
        # sys.exit()

    if PAUSED:
        print('GAME IS PAUSED')
        # ALL_SPRITES.stop()
        while PAUSED:
            SCREEN.fill((255, 255, 255))
            paused_HUD.draw(SCREEN)
            for event in pygame.event.get():
                """
                Event checking/handling.
                """
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        PAUSED = not PAUSED
                        # ALL_SPRITES.move()

    # remove enemies and spawn boss if score threshold is reached 
    if player.score >= SPAWN_BOSS_SCORE:
        for enemy in enemy_group:
            enemy.kill()

        # spawn
        print(spawned_boss)
        if not spawned_boss:
            spawn_regular_enemies = False
            boss_group.add(boss)
            ALL_SPRITES.add(boss)
            spawned_boss = True

    # every 3 seconds, spawn a new enemy
    if now - before > 3 and spawn_regular_enemies:
        """
        Enemy spawn rate.
        """
        before = now
        new_enemy = Enemyship(ENEMIES[random.randint(0, len(ENEMIES) - 1)])
        enemy_group.add(new_enemy)
        ALL_SPRITES.add(new_enemy)

    # check for events
    for event in pygame.event.get():
        """
        Event checking/handling.
        """
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                PAUSED = not PAUSED
                # print(PAUSED)

                # PAUSED = True
                # while PAUSED:
                #     for event in pygame.event.get():
                #         if event.key == pygame.K_ESCAPE:
                #             PAUSED = False
                #     SCREEN.fill((255, 255, 255))

    # collision between a player and an enemy
    if pygame.sprite.groupcollide(player_group, enemy_group, False, True):
        """
        Player crashed into a ship.
        """
        player.lives -= 1
        lives_HUD.update('x{}'.format(player.lives))

    # collision between an enemy's bullets and the player
    if pygame.sprite.groupcollide(player_group, enemy_bullet_group, False, True):
        """
        Player died to enemy fire.
        """
        player.lives -= 1
        lives_HUD.update('x{}'.format(player.lives))

    # collision between player's bullets and enemies
    if pygame.sprite.groupcollide(player_bullet_group, enemy_group, True, True):
        """
        Player killed an enemy. Spawns a new enemy whenever the player kills an enemy.
        """ 
        player.score += 100
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
        lives_HUD.update('x{}'.format(player.lives))

    # collision between player's bullets and boss
    if pygame.sprite.groupcollide(player_bullet_group, boss_group, False, False):
        """
        Player's bullets collide with boss.
        """
        boss.health -= 10
        boss_health_HUD.update(text = '{:,}/10,000'.format(boss.health))

    # collision between the boss' bullets and the player
    if pygame.sprite.groupcollide(boss_bullet_group, player_group, False, False):
        player.lives -= 1
        lives_HUD.update('x{}'.format(player.lives))

    # draw HUD elements to screen
    if SHOW_PLAYER_HUD:
        lives_HUD.draw(SCREEN)
        score_HUD.draw(SCREEN)
    
    # draw win screen if player won
    if player.has_won:
        win_HUD.draw(SCREEN)
        SHOW_PLAYER_HUD = False

    # draw lose screen if player lost
    if player.has_lost:
        game_over_HUD.draw(SCREEN)
        SHOW_PLAYER_HUD = False

    # draw boss health if boss has spawned
    if boss.is_alive and spawned_boss:
        boss_health_HUD.draw(SCREEN)

    # draws all sprites to screen
    ALL_SPRITES.draw(SCREEN)
    
    # updates the position of all sprites (i.e. moving surfaces)
    ALL_SPRITES.update(dt)

    # update pygame
    pygame.display.update()