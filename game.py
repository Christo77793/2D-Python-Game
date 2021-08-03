import pygame

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

# Defining player actions
moving_left = False
moving_right = False

# Define colors
BG = (250, 250, 210)


# Function to update the background
def draw_bg():
    screen.fill(BG)


# Player; change char name
class Soldier(pygame.sprite.Sprite):

    def __init__(self, character_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)

        self.character_type = character_type

        self.speed = speed
        self.direction = 1  # looking to the right
        self.flip = False

        img = pygame.image.load(f'img/{self.character_type}/Idle/0.png')
        self.image = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
        self.rectangle = self.image.get_rect()
        self.rectangle.center = (x, y)

    def move(self, fn_moving_left, fn_moving_right):

        # reset movement var; dx, dy = delta x & y
        dx = 0
        dy = 0

        # print(f"fn_moving_left: {fn_moving_left}")
        # print(f"fn_moving_right: {fn_moving_right}")

        # assign movement var if moving towards left/right
        if fn_moving_left:
            dx = -self.speed

            self.flip = True
            self.direction = -1

        if fn_moving_right:
            dx = self.speed

            self.flip = False
            self.direction = 1

        # update rectangle position
        self.rectangle.x += dx
        self.rectangle.y += dy

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

    # draw character
    player.draw()
    enemy.draw()

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
