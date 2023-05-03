import pygame
import math
import random
import os
from enemy import Enemy
import button
import Main_Menu

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Lossi kaitsmine')
pygame.mixer.music.load("ajalooline.mp3")
pygame.mixer.music.play(-1)



clock = pygame.time.Clock()
FPS = 60

level = 1
kõrgskoor = 0
level_difficulty = 0
target_difficulty = 1000
DIFFICULTY_MULTIPLIER = 1.1
game_over = False
next_level = False
ENEMY_TIMER = 1000
last_enemy = pygame.time.get_ticks()
enemies_alive = 0
max_towers = 4
TOWER_COST = 5000
tower_positions = [
[SCREEN_WIDTH - 250, SCREEN_HEIGHT - 200],
[SCREEN_WIDTH - 200, SCREEN_HEIGHT - 150],
[SCREEN_WIDTH - 150, SCREEN_HEIGHT - 150],
[SCREEN_WIDTH - 100, SCREEN_HEIGHT - 150],
]


if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())

WHITE = (255, 255, 255)
GREY = (100, 100, 100)

font = pygame.font.SysFont('Futura', 30)
font_60 = pygame.font.SysFont('Futura', 60)


taust = pygame.image.load('taust.png').convert_alpha()
castle_img_100 = pygame.image.load('loss_100.png').convert_alpha()
castle_img_50 = pygame.image.load('loss_50.png').convert_alpha()
castle_img_25 = pygame.image.load('loss_25.png').convert_alpha()

tower_img_100 = pygame.image.load('torn_100.png').convert_alpha()
tower_img_50 = pygame.image.load('torn_50.png').convert_alpha()
tower_img_25 = pygame.image.load('torn_25.png').convert_alpha()

bullet_img = pygame.image.load('kuul.png').convert_alpha()
b_w = bullet_img.get_width()
b_h = bullet_img.get_height()
bullet_img = pygame.transform.scale(bullet_img, (int(b_w * 0.075), int(b_h * 0.075)))

enemy_animations = []
enemy_types = ['knight.png', 'goblin.png', 'purple_goblin.png', 'red_goblin.png']
enemy_types2 = ['knight2.png', 'goblin2.png', 'purple_goblin2.png', 'red_goblin2.png']
enemy_health = [150, 125, 100, 50]
enemy_speed = [1, 1.2, 1.5, 2]

animation_types = ['walk', 'attack', 'death']
for enemy in enemy_types:

    animation_list = []
    for animation in animation_types:
        


        temp_list = []

        num_of_frames = 20
        
        for i in range(num_of_frames):
            if animation == 'walk' or animation == 'attack':
                img = pygame.image.load(enemy).convert_alpha()
            else:
                img = pygame.image.load(enemy_types2[enemy_types.index(enemy)]).convert_alpha()
            
            e_w = img.get_width()
            e_h = img.get_height()
            img = pygame.transform.scale(img, (int(e_w * 0.2), int(e_h * 0.2)))
            temp_list.append(img)
        animation_list.append(temp_list)
    enemy_animations.append(animation_list)

repair_img = pygame.image.load('parandamine.png').convert_alpha()
armour_img = pygame.image.load('kaitse.png').convert_alpha()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def show_info():
    draw_text('Raha: ' + str(castle.money), font, GREY, 10, 10)
    draw_text('Skoor: ' + str(castle.score), font, GREY, 180, 10)
    draw_text('Kõrgskoor: ' + str(high_score), font, GREY, 180, 30)
    draw_text('Level: ' + str(level), font, GREY, SCREEN_WIDTH // 2, 10)
    draw_text('Elud: ' + str(castle.health) + " / " + str(castle.max_health), font, GREY, SCREEN_WIDTH - 230, SCREEN_HEIGHT - 50)
    draw_text('1000', font, GREY, SCREEN_WIDTH - 220 , 70)
    draw_text(str(TOWER_COST), font, GREY, SCREEN_WIDTH - 150, 70)
    draw_text('500', font, GREY, SCREEN_WIDTH - 70 , 70)

class Castle():
    def __init__(self, image100, image50, image25, x, y, scale):
        self.health = 1000
        self.max_health = self.health
        self.fired = False
        self.money = 0
        self.score = 0

        width = image100.get_width()
        height = image100.get_height()

        self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
        self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
        self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y


    def shoot(self):
        pos = pygame.mouse.get_pos()
        x_dist = pos[0] - self.rect.midleft[0]
        y_dist = -(pos[1] - self.rect.midleft[1])
        self.angle = math.degrees(math.atan2(y_dist, x_dist))
        if pygame.mouse.get_pressed()[0] and self.fired == False and pos[1] > 70:
            self.fired = True
            bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
            bullet_group.add(bullet)
        if pygame.mouse.get_pressed()[0] == False:
            self.fired = False



    def draw(self):

        if self.health <= 250:
            self.image = self.image25
        elif self.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100

        screen.blit(self.image, self.rect)

    def repair(self):
        if self.money >= 1000 and self.health < self.max_health:
            self.health += 500
            self.money -= 1000
            if castle.health > castle.max_health:
                castle.health = castle.max_health

    def armour(self):
        if self.money >= 500:
            self.max_health += 250
            self.money -= 500



class Tower(pygame.sprite.Sprite):
    def __init__(self, image100, image50, image25, x, y, scale):
        pygame.sprite.Sprite.__init__(self)

        self.got_target = False
        self.angle = 0
        self.last_shot = pygame.time.get_ticks()

        width = image100.get_width()
        height = image100.get_height()

        self.image100 = pygame.transform.scale(image100, (int(width * scale), int(height * scale)))
        self.image50 = pygame.transform.scale(image50, (int(width * scale), int(height * scale)))
        self.image25 = pygame.transform.scale(image25, (int(width * scale), int(height * scale)))
        self.image = self.image100
        self.rect = self.image100.get_rect()
        self.rect.x = x
        self.rect.y = y


    def update(self, enemy_group):
        self.got_target = False

        for e in enemy_group:
            if e.alive:
                target_x, target_y = e.rect.midbottom
                self.got_target = True
                break

        if self.got_target:
            x_dist = target_x - self.rect.midleft[0]
            y_dist = -(target_y - self.rect.midleft[1])
            self.angle = math.degrees(math.atan2(y_dist, x_dist))

            shot_cooldown = 1000

            if pygame.time.get_ticks() - self.last_shot > shot_cooldown:
                self.last_shot = pygame.time.get_ticks()
                bullet = Bullet(bullet_img, self.rect.midleft[0], self.rect.midleft[1], self.angle)
                bullet_group.add(bullet)


        if castle.health <= 250:
            self.image = self.image25
        elif castle.health <= 500:
            self.image = self.image50
        else:
            self.image = self.image100



class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, x, y, angle):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.angle = math.radians(angle)
        self.speed = 10

        self.dx = math.cos(self.angle) * self.speed
        self.dy = -(math.sin(self.angle) * self.speed)


    def update(self):

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()         


        self.rect.x += self.dx
        self.rect.y += self.dy



class Crosshair():
    def __init__(self, scale):
        image = pygame.image.load('sihik.png').convert_alpha()
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()


        pygame.mouse.set_visible(False)


    def draw(self):
        mx, my = pygame.mouse.get_pos()
        self.rect.center = (mx, my)
        screen.blit(self.image, self.rect)




castle = Castle(castle_img_100, castle_img_50, castle_img_25, SCREEN_WIDTH - 250, SCREEN_HEIGHT - 300, 0.2)


crosshair = Crosshair(0.025)


repair_button = button.Button(SCREEN_WIDTH - 220, 10, repair_img, 0.5)
tower_button = button.Button(SCREEN_WIDTH - 140, 10, tower_img_100, 0.1)
armour_button = button.Button(SCREEN_WIDTH - 75, 10, armour_img, 1.5)


tower_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()



mäng_töötab = True
while mäng_töötab:

    clock.tick(FPS)

    if game_over == False:
        screen.blit(taust, (0, 0))


        castle.draw()
        castle.shoot()

        tower_group.draw(screen)
        tower_group.update(enemy_group)


        crosshair.draw()


        bullet_group.update()
        bullet_group.draw(screen)


        enemy_group.update(screen, castle, bullet_group)


        show_info()


        if repair_button.draw(screen):
            castle.repair()
        if tower_button.draw(screen):

            if castle.money >= TOWER_COST and len(tower_group) < max_towers:
                tower = Tower(
                    tower_img_100,
                    tower_img_50,
                    tower_img_25,
                    tower_positions[len(tower_group)][0],
                    tower_positions[len(tower_group)][1],
                    0.2
                    )
                tower_group.add(tower)

                castle.money -= TOWER_COST
        if armour_button.draw(screen):
            castle.armour()


        if level_difficulty < target_difficulty:
            if pygame.time.get_ticks() - last_enemy > ENEMY_TIMER:

                e = random.randint(0, len(enemy_types) -1)
                enemy = Enemy(enemy_health[e], enemy_animations[e], -100, (SCREEN_HEIGHT - random.randint(100,200)), enemy_speed[e])
                enemy_group.add(enemy)

                last_enemy = pygame.time.get_ticks()

                level_difficulty += enemy_health[e]



        if level_difficulty >= target_difficulty:

            enemies_alive = 0
            for e in enemy_group:
                if e.alive == True:
                    enemies_alive += 1

            if enemies_alive == 0 and next_level == False:
                next_level = True
                level_reset_time = pygame.time.get_ticks()


        if next_level == True:
            draw_text('Level läbitud!', font_60, WHITE, 200, 300)

            if castle.score > high_score:
                high_score = castle.score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            if pygame.time.get_ticks() - level_reset_time > 1500:
                next_level = False
                level += 1
                last_enemy = pygame.time.get_ticks()
                target_difficulty *= DIFFICULTY_MULTIPLIER
                level_difficulty = 0
                enemy_group.empty()


        if castle.health <= 0:
            game_over = True

    else:
        draw_text('Mäng läbi!', font, GREY, 300, 300)
        draw_text('Vajuta "A-d" Et uuesti mängida!', font, GREY, 250, 360)
        pygame.mouse.set_visible(True)
        key = pygame.key.get_pressed()
        
        
        if level == 11:
            game_over = True
            draw_text('Sa võitsid mängu!', font, GREY, 300, 300)
            draw_text('Vajuta "A-d" Et uuesti mängida!', font, GREY, 250, 360)
            pygame.mouse.set_visible(True)
            key = pygame.key.get_pressed()

        
        
        if key[pygame.K_a]:

            game_over = False
            level = 1
            target_difficulty = 1000
            level_difficulty = 0
            last_enemy = pygame.time.get_ticks()
            enemy_group.empty()
            tower_group.empty()
            castle.score = 0
            castle.health = 1000
            castle.max_health = castle.health
            castle.money = 0
            pygame.mouse.set_visible(False)




    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mäng_töötab = False


    pygame.display.update()

pygame.quit()