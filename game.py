import pygame
import os  # used to count number of files in a folder

pygame.init()

# Setting Resolution
screen_width = 800
# screen_height = int(screen_width * 0.8)
screen_height = int(screen_width * 0.7)

screen = pygame.display.set_mode((screen_width, screen_height))

# Setting Game Title
pygame.display.set_caption('First 2D Game')

# Set FrameRate
clock = pygame.time.Clock()
FPS = 60

# Game Var
gravity = 0.75

# Defining player actions
moving_left = False
moving_right = False
shoot = False

# Load images
# 1. Bullets
bullet_img = pygame.image.load(f'img/icons/bullet.png').convert_alpha()

# Define colors
BG = (250, 250, 210)
Red = (255, 0, 0)


# Function to update the background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, Red, (0, 300), (screen_width, 300))


# Player; change char name
class Soldier(pygame.sprite.Sprite):

    def __init__(self, character_type, x, y, scale, speed, ammo):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True

        self.character_type = character_type

        self.ammo = ammo
        self.start_ammo = ammo  # this will not change

        self.speed = speed
        self.direction = 1  # looking to the right
        self.vel_y = 0  # no initial speed to begin with

        self.shoot_cooldown = 0

        self.health = 100 # we can add custom health by adding health as arg
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

        if pygame.sprite.spritecollide(enemy, bullet_groups, False):

            # if shot reduce player health
            enemy.health -= 25

            if enemy.alive:
                # if the bullet hits a player or an enemy it gets killed
                self.kill()


# creating Sprite groups
bullet_groups = pygame.sprite.Group()

# Player Location
player = Soldier('player', 200, 300, 2, 5, 21)
enemy = Soldier('enemy', 400, 270, 2, 5, 21)

run = True
while run:

    clock.tick(FPS)  # setting max FPS

    draw_bg()  # update background each iteration

    # updating animation
    player.update()
    enemy.update()

    # draw character
    player.draw()
    enemy.draw()

    # update and draw groups
    bullet_groups.update()
    bullet_groups.draw(screen)

    # update player actions
    if player.alive:

        # shoot bullets
        if shoot:
            player.shoot()

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

            if event.key == pygame.K_SPACE:
                shoot = True

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

            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
