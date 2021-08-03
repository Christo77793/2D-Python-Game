import pygame
import os  # used to count number of files in a folder

pygame.init()

# Setting Resolution
screen_width = 800
screen_height = int(screen_width * 0.8)

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

# Define colors
BG = (250, 250, 210)
Red = (255, 0, 0)


# Function to update the background
def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, Red, (0, 300), (screen_width, 300))


# Player; change char name
class Soldier(pygame.sprite.Sprite):

    def __init__(self, character_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)

        self.alive = True

        self.character_type = character_type

        self.speed = speed
        self.direction = 1  # looking to the right
        self.vel_y = 0  # no initial speed to begin with

        self.jump = False
        self.flip = False
        self.in_air = True

        self.animation_list = []
        self.frame_index = 0
        self.action = 0  # idle or run

        self.update_time = pygame.time.get_ticks()

        # loading all images for the animation
        animation_types = ["Idle", "Run", "Jump"]

        for animation in animation_types:

            # counts the number of frames
            number_of_frames = len(os.listdir(f'img/{self.character_type}/{animation}'))

            temp_list = []

            for char_image in range(number_of_frames):
                image = pygame.image.load(f'img/{self.character_type}/{animation}/{char_image}.png')
                image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
                temp_list.append(image)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rectangle = self.image.get_rect()
        self.rectangle.center = (x, y)

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
        if self.rectangle.bottom + dy > 300:
            dy = 300 - self.rectangle.bottom
            self.in_air = False

        # update rectangle position
        self.rectangle.x += dx
        self.rectangle.y += dy

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
            self.frame_index = 0

    def update_action(self, new_action):

        # check if the new action is different from the previous action
        if new_action != self.action:
            self.action = new_action

            # restart animation
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(
            pygame.transform.flip(
                self.image,  # image to flip
                self.flip,  # flip it in the x axis; will execute only if self.flip is true
                False  # flip it in the y axis
            ),
            self.rectangle
        )


# Player Location
player = Soldier('player', 200, 200, 2, 5)
enemy = Soldier('enemy', 300, 300, 2, 5)

run = True
while run:

    clock.tick(FPS)  # setting max FPS

    draw_bg()  # update background each iteration

    player.update_animation()  # updating animation

    # draw character
    player.draw()
    enemy.draw()

    # update player actions
    if player.alive:
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

    pygame.display.update()

pygame.quit()
