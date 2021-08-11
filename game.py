import pygame
import os  # used to count number of files in a folder

pygame.init()

# Setting Resolution
screen_width = 800
screen_height = int(screen_width * 0.8)
# screen_height = int(screen_width * 0.7)

screen = pygame.display.set_mode((screen_width, screen_height))

# Setting Game Title
pygame.display.set_caption('First 2D Game')

# Set FrameRate
clock = pygame.time.Clock()
FPS = 60

# Game Var
gravity = 0.75
title_size = 40

# Defining player actions
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# Loading images

# 1. Bullets
bullet_img = pygame.image.load(f'img/icons/bullet.png').convert_alpha()

# 2. Grenade
grenade_img = pygame.image.load(f'img/icons/grenade.png').convert_alpha()

# 3. Pickup boxes
health_box_img = pygame.image.load(f'img/icons/health_box.png').convert_alpha()  # health
ammo_box_img = pygame.image.load(f'img/icons/ammo_box.png').convert_alpha()  # ammo
grenade_box_img = pygame.image.load(f'img/icons/grenade_box.png').convert_alpha()  # grenade

item_boxes = {
    'Health': health_box_img,
    'Ammo': ammo_box_img,
    'Grenade': grenade_box_img
}

# Define colors
BG = (250, 250, 210)  # background
Red = (255, 0, 0)
Blue = (0, 0, 255)
Green = (0, 250, 0)
White = (255, 255, 255)
Black = (0, 0, 0)


# Function to update the background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, Red, (0, 300), (screen_width, 300))


# define fonts
font = pygame.font.SysFont('Imprint MT Shadow', 30)


# Function to draw text on screen
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


# Player; change char name
class Soldier(pygame.sprite.Sprite):

    def __init__(self, character_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True

        self.character_type = character_type

        self.ammo = ammo
        self.start_ammo = ammo  # this will not change
        self.grenades = grenades

        self.speed = speed
        self.direction = 1  # looking to the right
        self.vel_y = 0  # no initial speed to begin with

        self.shoot_cooldown = 0

        self.health = 100  # we can add custom health by adding health as arg
        self.max_health = self.health

        self.jump = False
        self.flip = False
        self.in_air = True

        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # idle or run

        self.update_time = pygame.time.get_ticks()

        # loading all images for the animation
        animation_types = ["Idle", "Run", "Jump", "Death"]

        for animation in animation_types:

            # counts the number of frames
            number_of_frames = len(os.listdir(f'img/{self.character_type}/{animation}'))

            temp_list = []

            for char_image in range(number_of_frames):
                image = pygame.image.load(f'img/{self.character_type}/{animation}/{char_image}.png').convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):

        # calling the update animation fn
        self.update_animation()
        self.check_alive()

        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, fn_moving_left, fn_moving_right):

        # reset movement var; dx, dy = delta x & y
        dx = 0
        dy = 0

        # assign movement var if moving towards left/right
        if fn_moving_left:
            dx = -self.speed

            self.flip = True
            self.direction = -1

        if fn_moving_right:
            dx = self.speed

            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vel_y = -11  # jump height
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += gravity

        if self.vel_y > 10:
            self.vel_y

        dy += self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.in_air = False

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):

        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20  # control bullet gap

            bullet = Bullet(
                self.rect.centerx + (0.6 * self.rect.size[0] * self.direction),
                # setting the bullet to come in front of the player based on the direction
                # direction is -ve or +ve
                self.rect.centery,
                self.direction
            )
            bullet_groups.add(bullet)

            # reduce ammo
            self.ammo -= 1

    def throw_grenade(self):

        grenade = Grenade(self.rect.centerx + (0.4 * self.rect.size[0] * self.direction),
                          self.rect.top,  # throwing the grenade in a trajectory
                          self.direction)

        grenade_groups.add(grenade)

        # reduce grenades
        self.grenades -= 1

    def update_animation(self):
        animation_cooldown = 100  # 100 milliseconds

        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1  # updating frame

        # if the animation is done, reset to the start
        if self.frame_index >= len(self.animation_list[self.action]):

            # stop animation if dead
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1

            # rest of animation
            else:
                self.frame_index = 0

    def update_action(self, new_action):

        # check if the new action is different from the previous action
        if new_action != self.action:
            self.action = new_action

            # restart animation
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):

        if self.health <= 0:
            self.health = 0  # setting it as 0 to avoid errors
            self.speed = 0
            self.alive = False

            self.update_action(3)

    def draw(self):
        screen.blit(
            pygame.transform.flip(
                self.image,  # image to flip
                self.flip,  # flip it in the x axis; will execute only if self.flip is true
                False  # flip it in the y axis
            ),
            self.rect
        )


class HealthBar():

    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):

        # update with new health
        self.health = health

        # calculating ratio
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, Black, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, Red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, Green, (self.x, self.y, 150 * ratio, 20))


class ItemBox(pygame.sprite.Sprite):

    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)

        self.item_type = item_type

        self.image = item_boxes[self.item_type]

        self.rect = self.image.get_rect()
        self.rect.midtop = (x + (title_size // 2), y + (title_size - self.image.get_height()))

    def update(self):

        # check if the player has reached the item (only player)
        if pygame.sprite.collide_rect(self, player):

            # check what kind of box
            if self.item_type == 'Health':
                player.health += 25

                # if health is greater than max health
                if player.health > player.max_health:
                    player.health = player.max_health

            elif self.item_type == 'Ammo':
                player.ammo += 9

            elif self.item_type == 'Grenade':
                player.grenades += 5

            # once collected delete the item
            self.kill()


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.speed = 10
        self.image = bullet_img

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.direction = direction

    def update(self):
        # move bullets
        self.rect.x += (self.direction * self.speed)

        # check if bullets are gone out of the screen
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()  # save memory

        # check collision with other characters
        if pygame.sprite.spritecollide(
                player,  # checks the sprite, player
                bullet_groups,  # check which group has been collided with
                False  # to not delete
        ):  # spritecollide checks if the sprite collides with a group
            if player.alive:
                # if shot reduce player health
                player.health -= 5

                # if the bullet hits a player or an enemy it gets killed
                self.kill()

        for enemy in enemy_group:

            if pygame.sprite.spritecollide(enemy, bullet_groups, False):

                # if shot reduce player health
                enemy.health -= 25

                if enemy.alive:
                    # if the bullet hits a player or an enemy it gets killed
                    self.kill()


class Grenade(pygame.sprite.Sprite):

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.timer = 100  # can change if adding different types of grenade

        self.vel_y = -11  # change grenade throw height
        self.horizontal_speed = 7

        self.image = grenade_img

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.direction = direction

    def update(self):
        self.vel_y += gravity
        dx = self.direction * self.horizontal_speed
        dy = self.vel_y

        # check collision with floor
        if self.rect.bottom + dy > 300:
            dy = 300 - self.rect.bottom
            self.horizontal_speed = 0

        # check collision with the wall
        if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
            self.direction *= -1

        # update grenade position
        self.rect.x += dx
        self.rect.y += dy

        # countdown timer
        self.timer -= 1.75  # modify to change time taken to explode after thrown

        if self.timer <= 0:
            self.kill()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            # do damage to nearby objects (players & enemies)

            if abs(self.rect.centerx - player.rect.centerx) < title_size * 2 and abs(self.rect.centery - player.rect.centery) < title_size * 2:
                # abs gives a +ve number even if the subtraction goes less than 0
                player.health -= 45

            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < title_size * 2 and abs(self.rect.centery - enemy.rect.centery) < title_size * 2:
                    # abs gives a +ve number even if the subtraction goes less than 0
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):

    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)

        self.images = []

        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), (int(img.get_height() * scale))))
            self.images.append(img)

        self.frame_index = 0
        self.image = self.images[self.frame_index]

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.counter = 0

    def update(self):
        explosion_speed = 3

        # update explosion animation
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1

            # if animation is complete then delete explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]


# creating Sprite groups

# object groups
bullet_groups = pygame.sprite.Group()
grenade_groups = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_boxes_group = pygame.sprite.Group()

# character groups
enemy_group = pygame.sprite.Group()

# Temp item boxes
item_box = ItemBox('Health', 100, 245)
item_boxes_group.add(item_box)
item_box = ItemBox('Ammo', 300, 245)
item_boxes_group.add(item_box)
item_box = ItemBox('Grenade', 500, 245)
item_boxes_group.add(item_box)

# Character Location

# player
player = Soldier('player', 200, 300, 2, 5, 21, 5)
health_bar = HealthBar(7, 15, player.health, player.health)

# enemy
enemy = Soldier('enemy', 400, 270, 2, 5, 21, 3)
enemy2 = Soldier('enemy', 500, 270, 2, 5, 21, 3)
enemy_group.add(enemy)
enemy_group.add(enemy2)

run = True
while run:

    clock.tick(FPS)  # setting max FPS

    draw_bg()  # update background each iteration

    # draw_text(f'Health: {player.health}', font, Black, 7, 15)  # show health
    health_bar.draw(player.health)  # show health

    draw_text(f'Ammo: ', font, Black, 7, 45)  # show ammo
    for x in range(player.ammo):
        screen.blit(bullet_img, (85 + (x * 10), 50))

    draw_text(f'Grenades: ', font, Black, 7, 65)  # show grenade
    for x in range(player.grenades):
        screen.blit(grenade_img, (115 + (x * 10), 70))

    player.update()  # updating animation
    player.draw()  # draw character

    for enemy in enemy_group:
        enemy.update()
        enemy.draw()

    # update and draw groups

    # bullets
    bullet_groups.update()
    bullet_groups.draw(screen)

    # grenade
    grenade_groups.update()
    grenade_groups.draw(screen)

    # explosion
    explosion_group.update()
    explosion_group.draw(screen)

    # items
    item_boxes_group.update()
    item_boxes_group.draw(screen)

    # update player actions
    if player.alive:

        # shoot bullets
        if shoot:
            player.shoot()

        # throw grenades
        elif grenade and grenade_thrown == False:  # using elif to avoid shooting and throwing grenades at the same time
            player.throw_grenade()
            grenade_thrown = True

        if player.in_air:
            player.update_action(2)  # 2: jump

        elif moving_left or moving_right:
            player.update_action(1)  # 1: run

        else:
            player.update_action(0)  # 0: idle

        player.move(moving_left, moving_right)  # change direction of the called instance (player/enemy)

    # events
    for event in pygame.event.get():

        # quit game
        if event.type == pygame.QUIT:
            run = False

        # keyboard input
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_a:
                moving_left = True

            if event.key == pygame.K_d:
                moving_right = True

            if event.key == pygame.K_q:
                shoot = True

            if event.key == pygame.K_e:
                grenade = True

            if event.key == pygame.K_w and player.alive:
                player.jump = True

            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard released
        if event.type == pygame.KEYUP:

            if event.key == pygame.K_a:
                moving_left = False

            if event.key == pygame.K_d:
                moving_right = False

            if event.key == pygame.K_q:
                shoot = False

            if event.key == pygame.K_e:
                grenade = False
                grenade_thrown = False

    pygame.display.update()

pygame.quit()
