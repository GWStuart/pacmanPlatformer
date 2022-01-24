import pygame
import random
import os  # Used to save files
import shutil  # Used to delete folders
import math  # Used to find distance between points
import datetime  # Used for the timer
pygame.init()  # Initialises python

title = "Pacman Platformer"  # Window title

with open("game_data/progress.txt") as p:  # Loads progress from the progress text file
    progress = int(p.read())  # Saves progress in progress variable


class Window:  # Responsible for the main python window
    LENGTH = 1280  # Window dimensions
    WIDTH = 720
    
    def __init__(self):  # Initialises the window
        self.win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Creates the full screen window
        pygame.display.set_caption(title)  # The window is named


class Button:  # Used for most buttons in the game
    click_sound = pygame.mixer.Sound("sounds/click.mp3")  # Button click sound
    click_sound.set_volume(2)  # volume is set to 2

    def __init__(self, win, img, pos, command, size_increase=15, select=False):  # Requires a few parameters
        self.win = win
        self.img = img  # Button image
        self.pos = pos
        self.size_increase = size_increase  # The size that the button will increase when hovered
        self.command = command  # The command that will be called when it is pressed
        self.select = select  # If the button is currently selected

        self.disable = False  # Disabled buttons will appear gray
        self.active = False  # Active buttons will appear yellow

        # Generates the normal and enlarged image
        self.img = (self.img, pygame.transform.scale(img, (img.get_width() + size_increase, img.get_height() +
                                                           size_increase)))
        self.mode = "small"

        # Button hit box. Defined by x, y, length, width
        self.hit_box = pygame.Rect(self.pos[0], self.pos[1], self.img[0].get_width(), self.img[0].get_height())

    def draw(self):  # Draws the button
        if self.mode == "small":  # Smaller button
            self.win.blit(self.img[0], self.pos)  # Button image is drawn
            if self.select and self.disable:  # Green box is drawn around "select" buttons
                pygame.draw.rect(self.win, (0, 255, 0), self.hit_box, 5)
        else:
            # Large button is drawn and centred on its position
            self.win.blit(self.img[1], (self.pos[0] - self.size_increase / 2, self.pos[1] - self.size_increase / 2))
            if self.select and self.disable:  # "select" button is in green
                pygame.draw.rect(self.win, (0, 255, 0), (self.pos[0] - self.size_increase / 2, self.pos[1] -
                                                         self.size_increase / 2, self.img[1].get_width(),
                                                         self.img[1].get_height()), 5)

    def move(self, pos):  # Moves the button to the desired x and y
        self.pos = pos  # Resets position then updates hit box
        self.hit_box = pygame.Rect(self.pos[0], self.pos[1], self.img[0].get_width(), self.img[0].get_height())

    def update(self, mouse, pressed):  # Responsible for hover and click detection
        if not pressed:
            self.active = True  # Activates buttons. This was done to fix a bug.

        if not self.active:  # If a button is not active
            self.draw()
            return  # This prevents further code from running
        if self.hit_box.colliderect(pygame.Rect(mouse[0], mouse[1], 1, 1)) and not self.disable:  # If touching mouse
            self.mode = "large"  # Grows larger
            if pressed:  # If the button is clicked
                Button.click_sound.play(0)  # Sound is played
                if self.command == 0:  # If there is no command then nothing happens
                    return True
                else:
                    self.command()  # Command is run
        else:
            self.mode = "small"  # If not touching mouse then mode is small
        self.draw()  # Button is drawn


class LevelBtn:  # Responsible for the built-in and custom buttons
    click_sound = pygame.mixer.Sound("sounds/click.mp3")  # Sound effect
    click_sound.set_volume(2)  # Volume is set to 2

    def __init__(self, win, x, y, main, delete, num=1, name=""):  # Requires a few parameters to initialise
        self.win = win
        self.x = x  # X and Y position
        self.y = y
        self.main = main  # If it is a main or custom button type
        self.num = num  # The leve number
        self.name = name  # The file location of the game data
        self.name_full = name  # Backup of file location is saved here

        if main == "custom":  # Find the personal best time from the game data
            self.pb = GameData.get_pb("game_data/custom/" + str(self.name_full))  # Uses get_pb function
        else:
            self.pb = GameData.get_pb("game_data/built_in/level" + str(num))
        if self.pb == "0":  # A PB of 0 is treated as N/A
            self.pb = "N/A"

        self.delete = delete
        self.delete_cooldown = 180  # Prevents levels being deleted accidentally

        self.length = 150  # Button length
        self.hit_box = pygame.Rect(self.x, self.y, self.length, self.length)  # Button hit box

        self.selected = False  # If the button is seleted
        if main == "main":  # If it is a normal built-in button
            self.disabled = num > (progress + 1)  # It is disabled if that level isn't unlocked
        else:
            self.disabled = False  # All custom levels are enabled
            if len(name) > 10:  # ... is used if names are greater than 10 characters
                self.name = name[:11] + "..."

        self.colour = (255, 255, 255)  # Normal colours: white
        self.selected_colour = (255, 255, 0)  # Selected colour: yellow
        self.disabled_colour = (66, 66, 66)  # Disabled colour: grey

        font = pygame.font.Font('freesansbold.ttf', 18)  # Font used to render PB text
        self.pb_text = font.render("PB: " + str(self.pb), True, self.selected_colour)  # Generates PB text
        if self.main == "main":  # A built-in level
            font = pygame.font.Font('freesansbold.ttf', 64)  # Font used to render level text
            self.text = font.render(str(num), True, self.colour)  # Default text
            self.selected_text = font.render(str(num), True, self.selected_colour)  # Selected text
            self.disabled_text = font.render(str(num), True, self.disabled_colour)  # Disabled text
        else:
            font = pygame.font.Font('freesansbold.ttf', 20)  # Font used to render level text
            self.text = font.render(self.name, True, (255, 255, 255))  # Default text
            self.selected_text = font.render(self.name, True, self.selected_colour)  # Selected text
            self.disabled_text = font.render(self.name, True, self.disabled_colour)  # Disabled text

            img = pygame.image.load("assets/play.png")
            self.play_btn = Button(self.win, img, (self.x + self.length/2 - img.get_width()/2, self.y+5), self.play)
            img = pygame.image.load("assets/edit.png")
            self.edit_btn = Button(self.win, img, (self.x + self.length/2 - img.get_width()/2, self.y+55), self.edit)
            img = pygame.image.load("assets/delete.png")
            self.delete_btn = Button(self.win, img, (self.x + self.length/2 - img.get_width()/2, self.y+105),
                                     self.remove)

    def play(self):  # When the play button has been pressed
        Game("game_data/custom/" + str(self.name_full), "normal")  # Creates a game class with the file location

    def edit(self):  # When edit button is pressed. Creates a game class in custom mode with the file location
        Game("game_data/custom/" + str(self.name_full), "custom")

    def remove(self):  # Removes the button
        if self.delete_cooldown <= 0:  # Cooldown prevents accidental deleting of buttons
            self.delete(self.name_full)

    def update(self, mouse, pressed):  # Main update of the button
        # Updates the PB time
        if self.main == "custom":  # Find the personal best time from the game data
            self.pb = GameData.get_pb("game_data/custom/" + str(self.name_full))  # Uses get_pb function
        else:
            self.pb = GameData.get_pb("game_data/built_in/level" + str(self.num))
        if self.pb == "0":  # A PB of 0 is treated as N/A
            self.pb = "N/A"
        font = pygame.font.Font('freesansbold.ttf', 18)  # Font used to render PB text
        self.pb_text = font.render("PB: " + str(self.pb), True, self.selected_colour)  # Generates PB text

        if self.disabled:  # Draws the button and its contents in gray
            pygame.draw.rect(self.win, self.disabled_colour, (self.x, self.y, self.length, self.length), 5)
            self.win.blit(self.disabled_text, (self.x + self.length / 2 - self.text.get_width() / 2, self.y +
                                               self.length / 2 - self.text.get_height() / 2))
        elif self.selected:  # Draws the button and its contents in yellow
            self.win.blit(self.pb_text, (self.x, self.y - self.pb_text.get_height() - 3))  # Render PB
            pygame.draw.rect(self.win, self.selected_colour, (self.x, self.y, self.length, self.length), 5)  # In Yellow
            if self.main == "main":  # Main button text
                self.win.blit(self.selected_text, (self.x + self.length / 2 - self.text.get_width() / 2, self.y +
                                                   self.length / 2 - self.text.get_height() / 2))
            else:  # Custom button text
                self.win.blit(self.selected_text, (self.x + self.length/2 - self.text.get_width() / 2, self.y +
                                                   self.length))
        else:  # Draws the normal button
            pygame.draw.rect(self.win, self.colour, (self.x, self.y, self.length, self.length), 5)  # Box is drawn
            if self.main == "main":  # Main button contents
                self.win.blit(self.text, (self.x + self.length / 2 - self.text.get_width() / 2, self.y +
                                          self.length / 2 - self.text.get_height() / 2))
            else:  # Custom button contents
                self.win.blit(self.text, (self.x + self.length / 2 - self.text.get_width() / 2, self.y + self.length))

        if self.hit_box.colliderect(pygame.Rect(mouse[0], mouse[1], 1, 1)) and not self.disabled:  # Touching mouse
            self.selected = True  # Selected is true and the button will therfore be drawn in yellow next frame
            if self.main == "custom":  # Three buttons are shown within the custom button
                self.play_btn.update(mouse, pressed)  # Each button is updated (and drawn)
                self.edit_btn.update(mouse, pressed)
                self.delete_btn.update(mouse, pressed)

            if pressed:
                if self.main == "main":
                    LevelBtn.click_sound.play(0)
                    Game("game_data/built_in/level" + str(self.num), "normal", self.num)
        else:  # If not touching mouse
            self.selected = False  # Selected is false

        self.disabled = self.num > (progress + 1)  # Checks that the player still hasn't unlocked the level

        if self.delete_cooldown > 0:  # Delete cooldown is decreased
            self.delete_cooldown -= 1


class FallingGhost:  # Responsible for the falling ghosts on the home screen
    def __init__(self, win):  # Only requires the window to initialise
        self.win = win
        # A random ghost in chosen using random.choice()
        self.img = pygame.image.load(f"assets/ghosts/{random.choice(['red', 'blue', 'orange', 'pink'])}.png")
        size = random.randint(20, 40)  # Random size from 20 to 40
        self.img = pygame.transform.scale(self.img, (size, size))  # Image is scaled to the given size
        self.x = random.randint(0, Window.LENGTH)  # X and Y are randomized
        self.y = -random.randint(0, window.WIDTH)

        self.y_vel = 1  # Starting y velocity is 1

    def draw(self):  # Draws and updates the ghost
        self.win.blit(self.img, (self.x, self.y))  # Ghost is drawn to the screen
        self.y += self.y_vel  # Y is increased by the y velocity
        if self.y > 0:  # Y velocity is increased by 0.1 each frame
            self.y_vel += 0.1
        if self.y > Window.WIDTH:  # If below screen
            self.x = random.randint(0, Window.LENGTH)  # X and Y is reset
            self.y = -random.randint(0, 50)
            self.y_vel = 1  # Y velocity is set back to 1


class Particle:  # Responsible for death effect particles
    def __init__(self, x, y, colour):  # Requires an x, y and colour
        self.x = x
        self.y = y
        self.colour = colour
        self.r = 10  # Default radius for the particles is 10 pixels

        self.x_vel = random.randint(-13, 13)  # A random x velocity and y velocity is chosen
        self.y_vel = random.randint(-17, -10)

    def draw(self, win):  # Draws and updates the particle
        pygame.draw.circle(win, self.colour, (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y), self.r)

        self.y += self.y_vel  # Applies gravity to the y values
        self.y_vel += 1
        self.x += self.x_vel  # Moves on the x and reduces the x velocity by 10%
        self.x_vel *= 0.9

        if (self.y - Game.SCROLL_Y) < Window.WIDTH + self.r:  # Detects if the particle is on screen or not
            return "alive"
        else:
            return "dead"  # If not the particle is considered dead


class Collectable:  # Responsible for collectables
    def __init__(self, x, y):  # Requires and x and y position
        self.x = x
        self.y = y
        self.eaten = False  # Keeps track of whether it is eaten or not

        self.counter = 0
        self.start_y = self.y  # Remembers the original y

        self.r = 7
        self.colour = (255, 255, 0)  # Yellow

        self.hit_box = (self.x - self.r, self.y - self.r, self.r * 2, self.r * 2)  # Collectable hit-box
        self.hit_box_colour = (0, 255, 0)  # Green

    def draw(self, win, hit_box=False, edit=False):  # Draws the collectable and hit box if "hit_box" is true
        if not self.eaten or edit:  # Only drawn if collectable is not eaten
            # Resets the hit-box
            self.hit_box = (self.x - Game.SCROLL_X - self.r, self.y - Game.SCROLL_Y - self.r, self.r * 2, self.r * 2)

            if self.eaten:
                pygame.draw.circle(win, (200, 200, 200), (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y), self.r)
            else:
                pygame.draw.circle(win, self.colour, (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y), self.r)  # draws

            if hit_box:  # If his_box is true then it draws the hit-box
                pygame.draw.rect(win, self.hit_box_colour, self.hit_box, 1)

    def touching_rect(self, rect1, edit=False):  # Detects if collectable is touching a rectangle
        if self.eaten and not edit:  # If eaten then just return False
            return False
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        return rect2.colliderect(rect1)  # Uses built int colliderect() method to detect collision

    def touching_pacman(self, rect):  # Detects if touching pacman
        if self.eaten:  # If eaten then just return False
            return False
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        rect = rect[0] - Game.SCROLL_X, rect[1] - Game.SCROLL_Y, rect[2], rect[3]  # Adjusts rect for scroll x and y
        return rect2.colliderect(rect)  # Uses built int colliderect() method to detect collision

    def update(self):  # Updates the collectable (moves it up and down)
        if Window.LENGTH > (self.x - Game.SCROLL_X) > (self.r * -2) and Window.WIDTH > (self.y - Game.SCROLL_Y) > \
                (self.r * -2) and not self.eaten:  # For efficiency it checks if the collectable is on screen
            self.y = self.start_y + math.sin(self.counter / 15) * 10
            self.counter += 1
            # Collectable movement on the y follows a sine wave where counter just counts up from 0
            if self.counter > 1000:  # Resets counter (This will result in a jitter but I don't know a better solution)
                self.counter = 0


class Platform:  # Base class for platform, bouncy, jump through and wall
    def __init__(self, x, y, length, width):  # Requires x, y, length and width
        self.x = x
        self.y = y
        self.length = length
        self.width = width
        self.colour = (0, 0, 255)  # Blue
        self.hit_box = pygame.Rect(self.x, self.y, self.length, self.width)  # Creates the hit-box
        self.hit_box_colour = (0, 255, 0)  # Green

    def draw(self, win, hit_box=False):  # Draws the platform
        # Draws the platform and two circles that make it look like rounded edges
        pygame.draw.rect(win, self.colour, (self.x-Game.SCROLL_X, self.y-Game.SCROLL_Y, self.length, self.width))
        pygame.draw.circle(win, self.colour, (self.x-Game.SCROLL_X, self.y-Game.SCROLL_Y+self.width / 2), self.width/2)
        pygame.draw.circle(win, self.colour, (self.x+self.length-Game.SCROLL_X, self.y+self.width/2-Game.SCROLL_Y),
                           self.width/2)
        if hit_box:  # Will draw the hit-box if "hit_box" is True
            pygame.draw.rect(win, self.hit_box_colour, (self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] -
                                                        Game.SCROLL_Y, self.hit_box[2], self.hit_box[3]), 1)

    def touching_pacman(self, rect):  # Uses built in colliderect to test if two rectangles collide
        return self.hit_box.colliderect(rect)

    def touching_rect(self, rect1):  # Tests for the collision of two rectangles (accounts for scrolling)
        rect2 = pygame.Rect((self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] - Game.SCROLL_Y, self.hit_box[2],
                             self.hit_box[3]))  # Updates rect for scrolling
        return rect2.colliderect(rect1)  # Uses builtin colliderect method


class Bouncy(Platform):  # Responsible for bouncy platforms (inherits from platform class)
    def __init__(self, x, y, length, width):
        super().__init__(x, y, length, width)  # Runs the __init__ method of the super class (ie Platform.__init__())
        self.colour = (255, 255, 0)  # Overwrites the colour to be yellow


class JumpThrough(Platform):  # Responsible for jump through platforms (inherits from platform class)
    def __init__(self, x, y, length, width):
        super().__init__(x, y, length, width)  # Runs the __init__ method of the super class (ie Platform.__init__())
        self.colour = (140, 137, 129)  # Overwrites the colour to be grey


class Wall(Platform):  # Responsible for walls (inherits from platform class)
    def draw(self, win, hit_box=False):  # Overwrites the draw method
        # Doesn't have rounded edges like other platforms
        pygame.draw.rect(win, self.colour, (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.length, self.width))
        if hit_box:  # Draws hit-box like in the Platform class
            pygame.draw.rect(win, self.hit_box_colour, (self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] -
                                                        Game.SCROLL_Y, self.hit_box[2], self.hit_box[3]), 1)


class Spike:  # Responsible for spikes in the game
    def __init__(self, x, y, num, flip=0):  # Requires an x, y, num and flip (which is 0 or 1)
        self.x = x
        self.y = y
        self.num = int(num)  # the number of spikes must be an integer
        self.flip = flip

        self.spike_len = 30  # Default size of a spike is 30 base and 30 height
        self.spike_height = 30
        if flip:  # If flip is true (ie a 1) then the height is negative because the spike goes down
            self.spike_height *= -1

        self.colour = (255, 255, 255)  # White

        self.hit_box_variance = 3  # Hit-box has a variance of 3 (Helps to make it more user friendly)
        self.hit_box_colour = (0, 255, 0)  # Green

        # Defines the hit-box taking into account the variance
        self.hit_box = pygame.Rect(self.x+self.hit_box_variance, self.y - self.spike_height,
                                   self.spike_len * self.num - (self.hit_box_variance*2), self.spike_height)

    def draw(self, win, hit_box=False):  # Draws the spikes
        pygame.draw.line(win, self.colour, (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y),
                         (self.x + (self.num * self.spike_len) - Game.SCROLL_X, self.y -
                          Game.SCROLL_Y), 5)  # Lines underneath the spikes
        for i in range(self.num):  # Loops over the number of spikes and draws the left side of the spike
            pygame.draw.line(win, self.colour, (self.x + (self.spike_len * i) - Game.SCROLL_X, self.y - Game.SCROLL_Y),
                             (self.x + (self.spike_len * i) + self.spike_len / 2 - Game.SCROLL_X, self.y -
                              self.spike_height - Game.SCROLL_Y), 5)
        for i in range(self.num):    # Loops over the number of spikes and draws the right side of the spike
            pygame.draw.line(win, self.colour, (self.x + (self.spike_len * i) + self.spike_len / 2 - Game.SCROLL_X,
                                                self.y - self.spike_height - Game.SCROLL_Y),
                             (self.x + (self.spike_len * (i+1)) - Game.SCROLL_X, self.y - Game.SCROLL_Y), 5)
        if hit_box:  # If hit-box is true then it draws the hit-box
            pygame.draw.rect(win, self.hit_box_colour, (self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] -
                                                        Game.SCROLL_Y, self.hit_box[2], self.hit_box[3]), 1)

    def touching_pacman(self, rect):  # Uses builtin colliderect method to test it ghost touches pacman
        return self.hit_box.colliderect(rect)  # Returns the collision result

    def touching_rect(self, rect1):  # Detects if collision with a rectangle
        rect2 = pygame.Rect(self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] - Game.SCROLL_Y,
                            self.hit_box[2], self.hit_box[3])  # Accounts for scroll x and scroll y
        return rect2.colliderect(rect1)  # Returns the collision result


class MovingPlatform:  # Responsible for moving platforms in the game
    def __init__(self, pos1, pos2, length, width, speed):  # Initialises the moving platform
        self.pos1 = pos1  # Start position
        self.pos2 = pos2  # End position
        self.length = length  # Platform length and width
        self.width = width
        self.speed = speed  # The speed that the platform moves

        self.direction = 1  # Either 1 or -1
        self.div_0 = self.pos2[0] - self.pos1[0] == 0  # Detects whether the two x's are the same: stop division 0 error
        self.pause = 0
        self.end_pause = 15

        self.colour = (255, 200, 0)  # Orange
        self.colour2 = (179, 179, 179)  # Grey

        self.x = pos1[0]  # X and Y are originally set to the position 1 coordinates
        self.y = pos1[1]

        self.hit_box = (self.x, self.y, self.length, self.width)  # Platform hit box
        self.hit_box_colour = (0, 255, 0)  # Green

    def draw(self, win, hit_box=False):  # Draws the platform on the screen
        self.draw_platform(win, self.x, self.y, self.colour)  # Platform is drawn
        # Updates hit box
        self.hit_box = pygame.Rect(self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.length, self.width)

        if hit_box:  # If "hit_box" is True then it will draw the hit-box
            pygame.draw.rect(win, self.hit_box_colour, self.hit_box, 1)

    def draw_platform(self, win, x, y, colour):  # Draws the actual moving platform
        # Consists of a rectangle with two circles that act as rounded corners
        pygame.draw.rect(win, colour, (x - Game.SCROLL_X, y - Game.SCROLL_Y, self.length, self.width))
        pygame.draw.circle(win, colour, (x - Game.SCROLL_X, y - Game.SCROLL_Y + self.width / 2), self.width / 2)
        pygame.draw.circle(win, colour, (x + self.length - Game.SCROLL_X, y + self.width / 2 - Game.SCROLL_Y),
                           self.width / 2)

    def draw_path(self, win, hit_box=False):  # Draws the path that the moving platform follows
        self.draw_platform(win, self.pos1[0], self.pos1[1], self.colour2)  # Starting position is drawn in gray
        self.draw_platform(win, self.pos2[0], self.pos2[1], self.colour2)  # Ending position is drawn in gray
        # Path line is drawn
        pygame.draw.line(win, self.colour2, (self.pos1[0] - Game.SCROLL_X + self.length/2, self.pos1[1] - Game.SCROLL_Y
                                             + self.width/2), (self.pos2[0] - Game.SCROLL_X + self.length/2,
                                                               self.pos2[1] - Game.SCROLL_Y + self.width/2))
        self.draw_platform(win, self.x, self.y, self.colour)  # The actual platform is drawn
        # Hit box is updated
        self.hit_box = pygame.Rect(self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.length, self.width)
        if hit_box:  # If "hit_box" is True then it will draw the hit-box
            pygame.draw.rect(win, self.hit_box_colour, self.hit_box, 1)

    def move_end(self, x, y):  # Moves the end position of the platform
        self.pos2 = x, y  # New end position is updated
        self.x, self.y = self.pos1  # Resets the platform at the start position
        self.div_0 = self.pos2[0] - self.pos1[0] == 0  # Detects whether the two x's are the same: stop division 0 error

    def touching_pacman(self, rect):  # Checks if the platform touches pacman
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        rect = rect[0] - Game.SCROLL_X, rect[1] - Game.SCROLL_Y, rect[2], rect[3]  # Updates rect for scroll x and y
        return rect2.colliderect(rect)  # Returns collision using the builtin colliderect method

    def touching_rect(self, rect1):  # Checks for collision with a rectangle
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        return rect2.colliderect(rect1)  # Uses builtin colliderect method

    def move(self):  # Moves the platform along its path
        if self.pause > 0:  # Pause variable is decreased until it hits 0
            self.pause -= 1
            return 0, 0  # Pacman and the platform are not moved

        if self.div_0:  # Prevents a division 0 error
            self.y += self.speed * self.direction
            change_x, change_y = 0, self.speed * self.direction  # Necessary change in x and y is calculated
        else:  # Note Sanjay Hingorani and Luke Sivyer helped me with the formula below
            # Uses trigonometry to calculated the required x and y change
            change_x = self.speed * math.cos(math.atan((self.pos2[1] - self.pos1[1]) / (self.pos2[0] - self.pos1[0])))\
                      * self.direction
            change_y = self.speed * math.sin(math.atan((self.pos2[1] - self.pos1[1]) /
                                                       (self.pos2[0] - self.pos1[0]))) * self.direction
            self.x += change_x  # x and y is updated accordingly
            self.y += change_y

        # The code below checks to see if the platform has reached the end and must turn back
        if self.x > max(self.pos1[0], self.pos2[0]):
            self.direction *= -1  # Direction is reversed
            self.pause = self.end_pause  # A pause is set (platform rests at each end)
            if max(self.pos1[0], self.pos2[0]) == self.pos1[0]:  # pos1 is bigger
                change_x, change_y = self.x - self.pos1[0], self.y - self.pos1[1]
                self.x, self.y = self.pos1
            else:
                change_x, change_y = self.x - self.pos2[0], self.y - self.pos2[1]
                self.x, self.y = self.pos2
        elif self.x < min(self.pos1[0], self.pos2[0]):
            self.direction *= -1  # Direction is reversed
            self.pause = self.end_pause  # A pause is set (platform rests at each end)
            if min(self.pos1[0], self.pos2[0]) == self.pos1[0]:  # pos1 is smaller
                change_x, change_y = self.x - self.pos1[0], self.y - self.pos1[1]  # Change is calculated
                self.x, self.y = self.pos1
            else:
                change_x, change_y = self.x - self.pos2[0], self.y - self.pos2[1]  # Change is calculated
                self.x, self.y = self.pos2
        elif self.y > max(self.pos1[1], self.pos2[1]):
            self.direction *= -1  # Direction is reversed
            self.pause = self.end_pause  # A pause is set (platform rests at each end)
            if max(self.pos1[1], self.pos2[1]) == self.pos1[1]:  # pos1 is bigger
                change_x, change_y = self.x - self.pos1[0], self.y - self.pos1[1]  # Change is calculated
                self.x, self.y = self.pos1
            else:
                change_x, change_y = self.x - self.pos2[0], self.y - self.pos2[1]  # Change is calculated
                self.x, self.y = self.pos2
        elif self.y < min(self.pos1[1], self.pos2[1]):
            self.direction *= -1  # Direction is reversed
            self.pause = self.end_pause  # A pause is set (platform rests at each end)
            if min(self.pos1[1], self.pos2[1]) == self.pos1[1]:  # pos1 is bigger
                change_x, change_y = self.x - self.pos1[0], self.y - self.pos1[1]  # Change is calculated
                self.x, self.y = self.pos1
            else:
                change_x, change_y = self.x - self.pos2[0], self.y - self.pos2[1]  # Change is calculated
                self.x, self.y = self.pos2

        if self.touching_pacman(Game.pacman.hit_box):  # If the platform touches pacman
            return change_x, change_y  # The necessary movements that pacman must make are returned
        else:
            return 0, 0  # Pacman is not moved


class Ghost:  # Responsible for all ghosts
    def __init__(self, x, y, colour):  # Requires x, y and colour (colour is either 0, 1, 2, of 3)
        self.is_dead = False
        self.type = int(colour)  # Colour must be an integer
        self.x = x
        self.y = y

        self.y_vel = 0
        self.direction = 0  # direction either 0 (right) or 1 (left)
        self.speed = 3
        self.r = 50
        self.max_wall = 20  # Max wall height that it can climb is 20 pixels

        self.colours = {0: "red", 1: "orange", 2: "pink", 3: "blue"}
        self.particles = []
        self.particle_colour = ((236, 28, 36), (255, 202, 24), (255, 174, 200), (0, 168, 243))[self.type]
        # particle colour is dependant on the colour of the ghost

        self.image = pygame.image.load("assets/ghosts/" + self.colours[self.type] + ".png")  # Load correct image
        self.image = pygame.transform.scale(self.image, (self.r, self.r))  # Scale the image down
        self.image = (self.image, pygame.transform.flip(self.image, True, False))  # Copy it and make a flipped version

        self.hit_box = (self.x, self.y, self.r, self.r)  # Creates the hit-box
        self.hit_box_colour = (0, 255, 0)  # Green

    def draw_particles(self, win):  # Will draw the ghost's particles when it dies
        states = []  # Keeps track of the state of each particle
        for particle in self.particles:  # Loops over particles
            state = particle.draw(win)
            states.append(state)  # If the particle is still on screen
        if "alive" not in states:  # If none of the particles are alive then it empties the particles list
            self.particles = []

    def draw(self, win, hit_box=False):  # Draws the ghost
        if self.is_dead:  # If the ghost is dead then it won't be drawn but instead the particles will be
            self.draw_particles(win)
            if len(self.particles) == 0:  # If the list has been emptied then the ghost it dead and removed
                Game.ghosts.remove(self)
            return  # Prevents further code from running

        # Redefines the hit-box and draws the ghost on the screen
        self.hit_box = pygame.Rect(self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.r, self.r)
        win.blit(self.image[self.direction], (self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y))

        if hit_box:  # If "hit_box" is True then it will draw the hit-box
            pygame.draw.rect(win, self.hit_box_colour, self.hit_box, 1)

    def touching_platform(self):  # Detects if the ghost touches a platform
        self.hit_box = pygame.Rect(self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.r, self.r)  # Redefines hit-box
        if self.y >= Window.WIDTH - self.r - 70:  # If the ghost is below the ground this counts as touching a platform
            return True
        for platform in Game.platforms:  # Loops over platforms and checks for collision
            if platform.touching_rect(self.hit_box):
                return platform  # returns that platform that was touched
        for platform in Game.jump_through:  # Loops over platforms and checks for collision
            if platform.touching_rect(self.hit_box):
                return platform  # returns that platform that was touched
        for platform in Game.moving_platforms:  # Loops over platforms and checks for collision
            if platform.touching_rect(self.hit_box):
                return True
        return False  # If there was no collision false is then returned

    def touching_rect(self, rect1):  # Checks for collision with a rectangle
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        return rect2.colliderect(rect1)  # Uses builtin colliderect method

    def touching_pacman(self, rect):  # Checks if the ghost touches pacman
        rect2 = pygame.Rect(self.hit_box)  # Creates a pygame Rect object
        rect = rect[0] - Game.SCROLL_X, rect[1] - Game.SCROLL_Y, rect[2], rect[3]  # Updates rect for scroll x and y
        return rect2.colliderect(rect)  # Returns collision using the builtin colliderect method

    def dead(self):  # Function is called when the ghost dies
        self.is_dead = True
        self.particles = [Particle(self.x + (self.r / 2), self.y + (self.r / 2), self.particle_colour)
                          for _ in range(20)]  # Creates 20 particles used in the death effect

    def wall(self, x):  # Checks if the ghost has run into a wall. Takes an x either -1 (left) or 1 (right)
        if self.touching_platform():  # This can only be the case if the ghost is touching a platform
            for i in range(self.max_wall):  # Moves the ghost up until it reaches the max wall height
                self.y -= 1
                if not self.touching_platform():  # If the ghost no longer touches a platform then no wall was detected
                    self.y += 1
                    return  # Just returns to exit the loop
            self.y += self.max_wall  # Moves the ghost back down
            self.x -= x * self.speed  # Moves the ghost back
            if self.direction == 0:  # Flips the direction from 0 to 1 or 1 to 0
                self.direction = 1
            else:
                self.direction = 0

    def touching_danger(self):  # Checks if ghost is touching a spike
        self.hit_box = pygame.Rect(self.x - Game.SCROLL_X, self.y - Game.SCROLL_Y, self.r, self.r)  # Updates hit-box
        for spike in Game.spikes:  # Loops over spikes and checks for collision
            if spike.touching_rect(self.hit_box):
                return spike  # Returns that spike that was touched
        return False  # If not spikes were touched then False is returned

    def update(self):  # Updates and moves the ghost
        if self.is_dead:  # If the ghost is dead then it doesn't update
            return

        self.y += self.y_vel  # Applies gravity using a y_vel
        self.y_vel += 1  # Gravity increases the longer you fall therefore y_vel is increased

        if self.touching_danger():  # It the ghost touches a spike it is dead
            self.dead()

        if self.touching_platform():  # If a platform was touched
            if self.y_vel < 0:  # Ie you are going up
                if str(type(self.touching_platform())) == "<class '__main__.JumpThrough'>":
                    return  # If you are going up and touch a JumpThrough you ignore it (ie go through it)
                while self.touching_platform():
                    self.y += 1  # Pushes the ghost down until it is no longer touching a platform
                self.y += 1
                self.y_vel = 0  # y_vel is reset to 0
                return

            while self.touching_platform():  # In this case you must be falling
                self.y -= 1  # Pushes the ghost up until it is no longer touching a platform
                self.y_vel = 0  # y_vel is reset to 0
            self.y += 1

            if self.direction == 0:  # Moves the ghost based of it's direction
                self.x += self.speed
                self.wall(1)  # Uses wall method to check if it touches a wall
            else:  # Left
                self.x -= self.speed
                self.wall(-1)  # Uses wall method to check if it touches a wall

            if not self.touching_platform():  # If not touching a platform (reached end of platform) then flip direction
                if self.direction == 0:  # Right
                    self.direction = 1
                    self.x -= self.speed  # Moves the ghost back
                else:  # Left
                    self.direction = 0
                    self.x += self.speed  # Moves the ghost back
        if str(type(self.touching_platform())) == "<class '__main__.Bouncy'>":
            self.y_vel = -25  # If touching a bounce pad then y_vel is negative (results in ghost going up)


class PacMan:  # Main class controlling pacman
    start_pos = (0, 0)  # Pacman spawn point
    score = 0  # Pacman score

    def __init__(self, x, y):  # Requires and x and y to initialise
        self.x = x
        self.y = y
        PacMan.start_pos = (x, y)  # Resets the start position to that x and y

        self.x_offset = 0  # X and Y offset cause by moving platforms
        self.y_offset = 0

        self.y_vel = 0
        self.r = 50  # Pacman radius
        self.speed = 7
        self.direction = 0  # Direction either 0 (right) or 1 (left)
        self.airtime = 5  # Counter that keeps track of the time in the air
        self.max_wall = 20  # Max wall height that it can climb is 20 pixels

        self.frames_per_animation = 5  # Frames per each pacman animation
        self.animation_cycle = 0  # The current animation cycle position

        images = [pygame.image.load(f"assets/pacman_{i}.png") for i in range(4)]  # Loads all 4 pacman images
        [images.append(pygame.image.load(f"assets/pacman_{3-i}.png")) for i in range(3)]  # Loads an additional 3 images
        # The two lines above load the full pacman cycle from - open to closed and back to open
        images = [pygame.transform.scale(image, (self.r, self.r)) for image in images]  # Scales images (using self.r)
        self.images = [(image, pygame.transform.flip(image, True, False)) for image in images]  # Flip image: left,right
        self.current_img = 0  # The current image. Just set to 0 for now

        self.hit_box_variance = 5  # Hit-box has a variance of 3 (Helps to make it more user friendly)
        self.hit_box = pygame.Rect(self.x + self.hit_box_variance, self.y, self.r - self.hit_box_variance * 2, self.r)
        self.hit_box_colour = (0, 255, 0)  # Green

        self.is_dead = False  # Is dead is set to false at the start of the program
        self.sound = pygame.mixer.Sound("sounds/pop.mp3")  # Loads the deaf sound effect
        self.sound.set_volume(2)
        self.particles = []  # These are the particles used in the death animation

    def draw(self, win, hit_box=False):
        if self.is_dead:  # If pacman is dead then it won't be drawn but instead the particles will be
            self.draw_particles(win)
            if len(self.particles) == 0:  # If the list has been emptied. (ie all particles are off screen)
                PacMan.score = 0  # Score is reset
                self.is_dead = False  # Player is alive again
                self.x, self.y = PacMan.start_pos[0], PacMan.start_pos[1]  # Respawns the player
                self.y_vel = 0
                self.airtime = 5
                for collectable in Game.collectables:  # Shows the collectables again
                    collectable.eaten = False
            return  # Breaks out of the method
        # The lines below draws pacman, at the current images and in the correct direction
        win.blit(self.images[self.current_img][self.direction], (self.x-Game.SCROLL_X, self.y-Game.SCROLL_Y))
        if hit_box:  # Draws the player hit-box if "hit_box" is True
            pygame.draw.rect(win, self.hit_box_colour, (self.hit_box[0] - Game.SCROLL_X, self.hit_box[1] -
                                                        Game.SCROLL_Y, self.hit_box[2], self.hit_box[3]), 1)

    def toggle_animation(self):  # Cycles through pacman's animations
        self.animation_cycle += 1  # Animation cycle is increased
        if self.animation_cycle == self.frames_per_animation:  # If those two numbers are divisible
            self.animation_cycle = 0  # Animation is reset (restarting the timer)
            self.current_img += 1
            if self.current_img > len(self.images) - 1:  # If this is the case the current image will loop back to 0
                self.current_img = 0

    def touching_platform(self):  # If pacman is touching a platform
        # resets the hit-box
        self.update_hit_box()
        if self.y >= Window.WIDTH - self.r - 70:  # If the ghost is below the ground this counts as touching a platform
            return True
        for platform in Game.platforms:  # Loops over platforms and checks for a collision
            if platform.touching_pacman(self.hit_box):
                return platform  # Returns that platform that was touched
        return self.touching_moving_platform()  # If there was no collision it then checks for moving platform collision

    def touching_moving_platform(self):  # Detects if pacman touches a moving platform
        self.update_hit_box()  # Hit box is updated
        for platform in Game.moving_platforms:  # Loops over moving platforms
            if platform.touching_pacman(self.hit_box):  # If there is a collision True is returned
                return True
        return False  # If there were no collisions False is returned

    def touching_danger(self):  # If pacman touches a danger (either spike or ghost)
        self.update_hit_box()
        for danger in Game.spikes:  # Loops over the spikes
            if danger.touching_pacman(self.hit_box):  # Detects collision using the hit-box
                return danger  # Returns the spike that was touched
        for ghost in Game.ghosts:  # Loops over the spikes
            if ghost.touching_pacman(self.hit_box):  # Detects collision using the hit-box
                return ghost  # Returns the ghost the was touched
        return False  # If there was no collision False is returned

    def touching_jump_through(self):  # Detects if pacman touches a jump through platform
        self.update_hit_box()
        for platform in Game.jump_through:  # Loops over the platforms
            if platform.touching_pacman(self.hit_box):  # Detects collision using the hit-box
                return platform  # Returns that platform that was touched
        return False  # If there was no collision False is returned

    def touching_collectable(self):  # If pacman touches a collectable
        self.update_hit_box()
        for collectable in Game.collectables:  # Loops over all collectables
            if collectable.touching_pacman(self.hit_box):  # Detects for collision using the hit-box
                collectable.eaten = True  # If eaten then the collectable is marked as eaten and score is increased
                PacMan.score += 1
                self.sound.play(0)  # Eating sound is played
        return False  # If no collectables were eaten then false is returned

    def wall(self, x):  # Checks if pacman has run into a wall. Takes an x either -1 (left) or 1 (right)
        if self.touching_platform() or self.touching_jump_through():  # If touching platform or jump through
            for i in range(self.max_wall):  # Moves pacman up until it reaches the max wall height
                self.y -= 1
                if not (self.touching_platform() or self.touching_jump_through()):  # No wall was detected
                    self.y += 1
                    return  # Just returns to exit the loop
            self.y += self.max_wall  # Moves pacman back down
            self.x -= x * self.speed  # Moves pacman back the direction it came

    def dead(self):  # Function is called when the pacman dies
        self.is_dead = True
        # Creates 20 particles used in the death effect
        self.particles = [Particle(self.x + (self.r / 2), self.y + (self.r / 2), (255, 255, 0)) for _ in range(20)]
        self.sound.play(5)  # Death sound is played

    def draw_particles(self, win):  # Will draw pacman particles when it dies
        states = []  # Keeps track of the state of each particle
        for particle in self.particles:  # Loops over particles
            state = particle.draw(win)
            states.append(state)  # If the particle is stilll visible
        if "alive" not in states:  # If none of the particles are alive then it empties the particles list
            self.particles = []
            Game.start_time = datetime.datetime.now()  # Game start time is then reset

    def set_pos(self, x, y):  # Resets the x, y and start position of pacman
        self.x = x
        self.y = y
        PacMan.start_pos = (x, y)  # New start position is defined

    def update_hit_box(self):  # Updates the pacman hit box
        self.hit_box = pygame.Rect(self.x + self.hit_box_variance, self.y, self.r - self.hit_box_variance * 2,
                                   self.r)

    def update(self, keys):  # Updates and moves pacman
        self.x_offset, self.y_offset = 0, 0  # X and Y offset is reset to 0
        for platform in Game.moving_platforms:  # Loops over moving platforms
            change = platform.move()
            self.x_offset += change[0]  # Each offset is added
            self.y_offset += change[1]
        self.x += self.x_offset  # PLayer x and y is moved according to the offsets
        self.y += self.y_offset

        if keys[pygame.K_r] and not self.is_dead:  # R is a reset keys
            self.dead()  # Kills the player (resets the game)
        if self.is_dead:  # If the player is dead it doesn't update
            return  # Exits the method

        self.y += self.y_vel  # Applies gravity with a y velocity
        self.y_vel += 1
        self.airtime += 1  # An airtime is calculated
        if self.y_vel >= self.r:  # Adds a maximum possible fall speed
            self.y_vel = self.r

        self.toggle_animation()  # Toggles pacman animation

        if self.touching_danger():  # If touching danger then pacman dies
            self.dead()
        self.touching_collectable()  # Checks for any collectables eaten

        if self.touching_platform() or (self.touching_jump_through() and self.y_vel > 0 and
                                        not (keys[pygame.K_DOWN] or keys[pygame.K_s])):
            if self.y_vel >= 0:  # Falling onto a platform
                while self.touching_platform() or self.touching_jump_through():
                    self.y -= 1  # Moves pacman up until it is no longer touching the ground
                self.y += 1
                self.airtime = 0  # Airtime is reset
            else:  # Jumping or on a bounce pad
                while self.touching_platform() or self.touching_jump_through():
                    self.y += 1  # Moves pacman down until pacman is not touching a platform
                self.y += 1
            self.y_vel = 0  # In either case the y velocity is reset to 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Moves left with either left key or a key
            self.x -= self.speed
            self.direction = 1  # 1 is for left
            self.wall(-1)  # Checks for walls with the wall function
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Moves right with either right key or d key
            self.x += self.speed
            self.direction = 0  # 0 is for right
            self.wall(1)  # Checks for walls with the wall function

        # Line bellow checks for up keys, w or space bar to see if user wants to jump
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.airtime <= 5 and self.y_vel >= -15:
            self.y_vel = -15  # Y vel is negative resulting in the player going up
        if str(type(self.touching_platform())) == "<class '__main__.Bouncy'>":  # Touching bounce pad
            self.y_vel = -25  # Y vel is also negative (player goes up)


class EditMode:  # Responsible for the game editor
    def __init__(self):
        # Value defaults held in a dictionary
        self.default = {"length": 100, "width": 14, "mode": 0, "spikes_num": 3, "spikes_flip": 0, "ghost_colour": 0,
                        "platform_speed": 3, "move_mode": "static"}

        # Define some variables (each with their own defaults)
        self.length = 100
        self.width = 14
        self.spikes_num = 3
        self.spikes_flip = 0
        self.ghost_colour = 0
        self.colour_held = False
        self.speed_held = False
        self.move_mode = "static"  # The mode of a moving platform (either static or dynamic)
        self.platform_speed = 3
        self.speed_font = pygame.font.Font("freesansbold.ttf", 20)  # The font used to display the score
        self.speed_text = self.speed_font.render(str(self.platform_speed), True, (255, 255, 255))  # Text for speed

        self.start_pos_img = pygame.image.load("assets/start_pos.png")  # Loads start pos image
        self.start_pos_img = pygame.transform.scale(self.start_pos_img, (Game.pacman.r, Game.pacman.r))  # Scales image

        # List of all object modes and cursor objects the will follow the cursor while the user is in edit mode
        self.modes = [Platform, Bouncy, Spike, JumpThrough, Ghost, Wall, MovingPlatform, Collectable, "start"]
        self.mode = 0
        self.cursor_object = [Platform(0, 0, 100, 14), Bouncy(0, 0, 100, 14), (Spike(0, 0, 3),
                                                                               Spike(0, 0, 3, flip=True)),
                              JumpThrough(0, 0, 100, 14),
                              (Ghost(0, 0, 0), Ghost(0, 0, 1), Ghost(0, 0, 2), Ghost(0, 0, 3)), Wall(0, 0, 100, 14),
                              MovingPlatform((0, 0), (1, 1), 100, 14, 3), Collectable(0, 0), "start"]

        self.increment_speed = 5
        self.scroll_speed = 10  # The scrolling speed to the arrow keys
        self.held = 0
        self.platform_cooldown = 0
        self.scroll_x = 0  # This scroll_x and scroll_y is different from Game.SCROLL_X and Game.SCROLL_Y
        self.scroll_y = 0

    def update(self, keys, win):  # Main loop for class
        win.blit(self.start_pos_img, (PacMan.start_pos[0] - Game.SCROLL_X, PacMan.start_pos[1] - Game.SCROLL_Y))

        mouse = pygame.mouse.get_pos()  # Gets mouse position

        Game.SCROLL_X = self.scroll_x  # Game.SCROLL_X is set to the scroll_x of the edit mode (also done for y)
        Game.SCROLL_Y = self.scroll_y

        # Backspace, delete or right click removes the object under the mouse
        if keys[pygame.K_BACKSPACE] or keys[pygame.K_DELETE] or pygame.mouse.get_pressed(3)[2]:
            rect = pygame.Rect(mouse[0] - 3, mouse[1] - 3, 6, 6)  # Creates a rectangle around the mouse (allowance 3)
            for platform in Game.platforms:  # Checks for collision with platforms
                if platform.touching_rect(rect):
                    Game.platforms.remove(platform)  # Removes the platform
            for spike in Game.spikes:  # Checks for collision with spikes
                if spike.touching_rect(rect):
                    Game.spikes.remove(spike)  # Removes the spike
            for platform in Game.jump_through:  # Checks for collision with jump through platforms
                if platform.touching_rect(rect):
                    Game.jump_through.remove(platform)  # Removes platform
            for ghost in Game.ghosts:  # Checks for collision with ghosts
                if ghost.touching_rect(rect):
                    Game.ghosts.remove(ghost)  # Removes ghost
            for collectable in Game.collectables:  # Checks for collision with collectables
                if collectable.touching_rect(rect, edit=True):
                    Game.collectables.remove(collectable)  # Removes collectable
            for platform in Game.moving_platforms:  # Checks for collision with moving platforms
                if platform.touching_rect(rect):
                    Game.moving_platforms.remove(platform)  # Removes the moving platform

        if keys[pygame.K_z] or pygame.mouse.get_pressed(3)[1]:  # Z key or middle mouse button works as a pick a block
            rect = pygame.Rect(mouse[0] - 3, mouse[1] - 3, 6, 6)  # Creates a rectangle around the mouse (allowance 3)
            for platform in Game.platforms + Game.jump_through:  # Checks for platforms and jump through platforms
                if platform.touching_rect(rect):
                    if str(type(platform)) == "<class '__main__.Bouncy'>":  # Bouncy
                        self.mode = 1
                    elif str(type(platform)) == "<class '__main__.JumpThrough'>":  # Jump through
                        self.mode = 3
                    elif str(type(platform)) == "<class '__main__.Wall'>":  # Wall
                        self.mode = 5
                    else:  # Standard platform
                        self.mode = 0
                    self.length = platform.length  # Length and width is set to be the same as the platform
                    self.width = platform.width
            for spike in Game.spikes:  # Checks for collision with spikes
                if spike.touching_rect(rect):
                    self.mode = 2
                    self.spikes_num = spike.num  # number and flip is set to the same as the spike
                    self.spikes_flip = spike.flip
            for ghost in Game.ghosts:  # Checks for collision with ghosts
                if ghost.touching_rect(rect):
                    self.mode = 4
                    self.ghost_colour = ghost.type  # Sets the colour to the same as the ghost
            for collectable in Game.collectables:  # Checks for collision with a collectable
                if collectable.touching_rect(rect, edit=True):
                    self.mode = 7  # Only sets the mode to the collectable mode
            for platform in Game.moving_platforms:  # Checks for collision with a moving platform
                if platform.touching_rect(rect):
                    self.mode = 6  # Sets it to platform mode
                    self.length = platform.length  # Length and width are set to the platform's length and width
                    self.width = platform.width

        if keys[pygame.K_t]:  # If "t" keys is pressed pacman is teleported to the mouse position
            if mouse[1] > Window.WIDTH - 70 - Game.pacman.r - Game.SCROLL_Y:  # If mouse below ground: pacman on ground
                Game.pacman.x, Game.pacman.y = mouse[0] + Game.SCROLL_X, Window.WIDTH - 70 - Game.pacman.r
                Game.pacman.update_hit_box()  # Updates the hit-box
            else:
                Game.pacman.x, Game.pacman.y = mouse[0] + Game.SCROLL_X, mouse[1] + Game.SCROLL_Y  # resets x and y
                Game.pacman.update_hit_box()  # Updates the hit-box

        if keys[pygame.K_1]:  # If a key is pressed then the mode will be set to that key
            self.mode = 0
        if keys[pygame.K_2]:
            self.mode = 1
        if keys[pygame.K_3]:
            self.mode = 2
        if keys[pygame.K_4]:
            self.mode = 3
        if keys[pygame.K_5]:
            self.mode = 4
        if keys[pygame.K_6]:
            self.mode = 5
        if keys[pygame.K_7]:
            self.mode = 6
        if keys[pygame.K_8]:
            self.mode = 7
        if keys[pygame.K_9]:
            self.mode = 8

        if keys[pygame.K_LEFT]:  # Arrow keys scroll the screen while in edit mode
            self.scroll_x -= self.scroll_speed
        if keys[pygame.K_RIGHT]:  # Right
            self.scroll_x += self.scroll_speed
        if keys[pygame.K_UP]:  # Up
            self.scroll_y -= self.scroll_speed
        if keys[pygame.K_DOWN]:  # Down
            self.scroll_y += self.scroll_speed

        if self.mode == 0 or self.mode == 1 or self.mode == 3 or self.mode == 5 \
                or (self.mode == 6 and self.move_mode == "static"):  # Platform type
            if keys[pygame.K_s]:  # WASD keys change the length and width
                self.width += self.increment_speed
            if keys[pygame.K_w]:  # Up
                self.width -= self.increment_speed
            if keys[pygame.K_d]:  # Right
                self.length += self.increment_speed
            if keys[pygame.K_a]:  # Left
                self.length -= self.increment_speed
            if self.width < 14:  # Platforms have min and max dimensions
                self.width = 14
            if self.length < 14:
                self.length = 14
            if self.width > 50 and self.mode != 5:  # Except mode 5 where there is no max width
                self.width = 50

        if self.mode == 2:  # Spike
            if not(keys[pygame.K_a] or keys[pygame.K_d]):
                self.held = 0
            else:  # A and D keys increase and decrease the number of spikes
                if keys[pygame.K_a] and (self.held == 0 or self.held < -30):
                    if self.spikes_num > 1:  # Number of spikes is decreased
                        self.spikes_num -= 1
                elif keys[pygame.K_d] and (self.held == 0 or self.held < -30):
                    self.spikes_num += 1  # Number of spikes is increased
                self.held -= 1
            if keys[pygame.K_w]:  # W and S keys flip the spikes
                self.spikes_flip = 0  # Up
            elif keys[pygame.K_s]:
                self.spikes_flip = 1  # Down

        if self.mode == 4:  # Ghost
            if keys[pygame.K_d]:  # D and A keys cycle through ghost colours
                if not self.colour_held:
                    self.colour_held = True
                    self.ghost_colour += 1  # Ghost colour is changed
                    if self.ghost_colour > 3:  # If colour is greater than 3 it resets to 0
                        self.ghost_colour = 0
            elif keys[pygame.K_a]:
                if not self.colour_held:
                    self.colour_held = True
                    self.ghost_colour -= 1  # Ghost colour is decreased
                    if self.ghost_colour < 0:  # If colour is less than 0 it resets to 3
                        self.ghost_colour = 3
            else:
                self.colour_held = False  # Ghost colour is not being held

        if self.mode == 6:  # A moving platform
            if keys[pygame.K_a]:  # A key
                if not self.speed_held:
                    self.speed_held = True
                    self.platform_speed -= 1  # Platform speed is decreased
                    if self.platform_speed < 1:  # If it is less than 1 then it is reset to 1
                        self.platform_speed = 1
            elif keys[pygame.K_d]:  # D key
                if not self.speed_held:
                    self.speed_held = True
                    self.platform_speed += 1  # Platform speed is increased
                    if self.platform_speed > 15:  # If it is more than 15 then it is reset to 15
                        self.platform_speed = 15
            else:
                self.speed_held = False  # No change in platform speed

        obj = self.cursor_object[self.mode]  # Gets the cursor object
        if self.mode == 8:  # Start pos
            if mouse[1] > Window.WIDTH - 70 - Game.pacman.r - Game.SCROLL_Y:  # If mouse is below ground
                win.blit(self.start_pos_img, (mouse[0], (Window.WIDTH - 70 - Game.pacman.r - Game.SCROLL_Y)))
            else:
                win.blit(self.start_pos_img, (mouse[0], mouse[1]))  # Draws the start pos at mouse position
            return
        elif self.mode == 2:  # Spike
            if self.spikes_flip:  # Accounts for normal and flipped spikes
                obj = obj[1]
            else:
                obj = obj[0]
        elif self.mode == 4:  # Ghost
            obj = obj[self.ghost_colour]  # Gets the relevant ghost colour
        elif self.mode == 6 and self.move_mode == "dynamic":  # A dynamic moving platform
            # Text that displays the platform speed
            self.speed_text = self.speed_font.render(f"Speed: {self.platform_speed}", True, (255, 255, 255))
            win.blit(self.speed_text, (5, Window.WIDTH - 25))  # Draws the speed text on teh screen

            if round(mouse[0] + Game.SCROLL_X) != round(obj.pos2[0]) or round(mouse[1] + Game.SCROLL_Y) != \
                    round(obj.pos2[1]):  # If the mouse has moved position
                obj.move_end(mouse[0] + Game.SCROLL_X, mouse[1] + Game.SCROLL_Y)  # THe endpoint is updated
                self.platform_cooldown = 5  # PLatform cooldown is set to 5

            obj.draw_path(win)  # Full path of platform is drawn
            obj.speed = self.platform_speed  # Object speed is saved
            if self.platform_cooldown > 0:
                self.platform_cooldown -= 1  # Cooldown is decreased
            else:
                obj.move()  # Platform is moved
            return  # No further code is run

        obj.x, obj.y = mouse[0] + Game.SCROLL_X, mouse[1] + Game.SCROLL_Y  # X and Y calculated. (using scroll x and y)

        if self.mode == 0 or self.mode == 1 or self.mode == 5 or self.mode == 3 or self.mode == 6:
            if obj.y > Window.WIDTH - 70 - self.width:  # If object is below the ground then it puts it on the ground
                obj.y = Window.WIDTH - 70 - self.width
        elif self.mode == 2:  # Spike
            # If spike is below the ground then it puts it on the ground
            if self.spikes_flip:  # When flipped it has a different hit-box
                if obj.y > Window.WIDTH - 70 - self.cursor_object[self.mode][0].spike_height:
                    obj.y = Window.WIDTH - 70 - self.cursor_object[self.mode][0].spike_height
            else:  # A normal (non flipped) spike
                if obj.y > Window.WIDTH - 70:  # Prevents spike below the ground
                    obj.y = Window.WIDTH - 70
        elif self.mode == 4:  # Ghost
            if obj.y > Window.WIDTH - 70 - Game.pacman.r:  # If object is below the ground then it puts it on the ground
                obj.y = Window.WIDTH - 70 - Game.pacman.r
        elif self.mode == 7:  # Collectable
            if obj.y > Window.WIDTH - 77:  # If object is below the ground then it puts it on the ground
                obj.y = Window.WIDTH - 77

        if self.mode == 0 or self.mode == 1 or self.mode == 3 or self.mode == 5 or self.mode == 6:  # Platform type
            obj.length, obj.width = self.length, self.width  # Length and width is set
        elif self.mode == 2:  # Spike
            obj.num = self.spikes_num  # Spike number is set
        obj.draw(win)  # Object is drawn

    def add_platform(self, x, y):
        x += Game.SCROLL_X  # X and Y is adjusted for the scroll x and y
        y += Game.SCROLL_Y
        # Lines below deal with stopping user from placing an object below the stage
        if self.mode == 0 or self.mode == 1 or self.mode == 5 or self.mode == 3 or self.mode == 6:  # Platforms
            if y > Window.WIDTH - 70 - self.width:  # If the platform is below ground it is drawn on the ground
                y = Window.WIDTH - 70 - self.width
        elif self.mode == 2:  # Spikes
            if self.spikes_flip:  # A flipped spike has a different hit box
                if y > Window.WIDTH - 70 - self.cursor_object[self.mode][0].spike_height:  # If below ground
                    y = Window.WIDTH - 70 - self.cursor_object[self.mode][0].spike_height
            else:  # Normal (non flipped) spikes
                if y > Window.WIDTH - 70:  # If below ground
                    y = Window.WIDTH - 70
        elif self.mode == 4:  # Ghosts
            if y > Window.WIDTH - 70 - Game.pacman.r:  # If below ground
                y = Window.WIDTH - 70 - Game.pacman.r
        elif self.mode == 8:  # Spawn point
            if y > Window.WIDTH - 70 - Game.pacman.r:  # If below ground
                y = Window.WIDTH - 70 - Game.pacman.r
        elif self.mode == 7:  # Collectable
            if y > Window.WIDTH - 77:  # If below ground
                y = Window.WIDTH - 77

        if self.mode == 0 or self.mode == 1 or self.mode == 5:  # Adds a platform
            Game.platforms.append(self.modes[self.mode](x, y, self.length, self.width))
        elif self.mode == 2:  # Adds a spike
            Game.spikes.append(self.modes[self.mode](x, y, self.spikes_num, flip=self.spikes_flip))
        elif self.mode == 3:  # Adds jump through
            Game.jump_through.append(self.modes[self.mode](x, y, self.length, self.width))
        elif self.mode == 4:  # Adds a ghost
            Game.ghosts.append(self.modes[self.mode](x, y, self.ghost_colour))
        elif self.mode == 8:  # Moves the start pos
            PacMan.start_pos = (x, y, self.ghost_colour)
        elif self.mode == 7:  # Adds a collectable
            Game.collectables.append(self.modes[self.mode](x, y))
        elif self.mode == 6:  # Adds a moving platform
            if self.move_mode == "static":
                self.move_mode = "dynamic"  # The mode is updates to dynamic
                self.cursor_object[self.mode].pos1 = (x, y)  # Stores the mouse pos as pos1
            else:  # Creates the moving object and adds it to the moving platforms list
                self.move_mode = "static"
                Game.moving_platforms.append(self.modes[self.mode](self.cursor_object[self.mode].pos1, (x, y),
                                                                   self.length, self.width, self.platform_speed))

    def reset(self):  # Resets values back to default (using the default dictionary)
        self.scroll_x = Game.SCROLL_X  # Scroll x and y is reset
        self.scroll_y = Game.SCROLL_Y
        self.held = 0
        self.length = self.default["length"]  # Defaults dictionary is used to find all of the default values
        self.width = self.default["width"]
        self.spikes_num = self.default["spikes_num"]
        self.spikes_flip = self.default["spikes_flip"]
        self.mode = self.default["mode"]
        self.ghost_colour = self.default["ghost_colour"]
        self.platform_speed = self.default["platform_speed"]
        self.move_mode = self.default["move_mode"]

    def drag(self, start, current):  # Moves the screen to the given x and y
        self.scroll_x += (start[0] - current[0]) - self.scroll_x  # Drags the screen by changing scroll x and y
        self.scroll_y += (start[1] - current[1]) - self.scroll_y


class GameData:  # Loads and saves game data
    @staticmethod
    def load_file(file, obj, lst):  # Reads "file", creates "obj" with file data, adds "obj" to "lst"
        with open(file, "r") as f:  # Reads the file and stores it in a variable f
            for line in f.readlines():  # Loops over each line of the file
                data = [float(i) for i in line.split()]  # Data is extracted and put into a list using split()
                lst.append(obj(*data))  # Object is created and added to the list (object is deconstructed using *)

    @staticmethod
    def save(location):  # Saves all game data
        if not location:  # If it is a new unnamed file
            number = 1  # Number is start as 1
            name = f"unnamed{number}"  # Creates a string called "unnamed" and a number
            while name in os.listdir("./game_data/custom"):  # Loops over directories until a valid one is found
                number += 1
                name = f"unnamed{number}"
            os.mkdir(os.path.join("./game_data/custom", name))  # Creates a new directory in custom folder
        else:
            name = location.split("/")[-1]  # Gets the final location name

        with open(os.path.join("./game_data/custom", name, "platform.txt"), "w") as f:  # Creates platform.txt
            # Filters out platforms to only contain default platforms and writes their data to the file
            for platform in list(filter(lambda x: str(type(x)) == "<class '__main__.Platform'>", Game.platforms)):
                f.write(f"{platform.x} {platform.y} {platform.length} {platform.width}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "bouncy.txt"), "w") as f:  # Creates bouncy.txt
            # Filters out platforms to only contain bouncy platforms and writes their data to the file
            for platform in list(filter(lambda x: str(type(x)) == "<class '__main__.Bouncy'>", Game.platforms)):
                f.write(f"{platform.x} {platform.y} {platform.length} {platform.width}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "wall.txt"), "w") as f:  # Creates wall.txt
            # Filters out platforms to only contain wall platforms and writes their data to the file
            for platform in list(filter(lambda x: str(type(x)) == "<class '__main__.Wall'>", Game.platforms)):
                f.write(f"{platform.x} {platform.y} {platform.length} {platform.width}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "jump_through.txt"), "w") as f:  # Creates jump_through.txt
            for platform in Game.jump_through:  # Loops over jump_through list and adds data
                f.write(f"{platform.x} {platform.y} {platform.length} {platform.width}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "spike.txt"), "w") as f:  # Creates spike.txt
            for spike in Game.spikes:  # Loops over spikes and adds their data
                f.write(f"{spike.x} {spike.y} {spike.num} {spike.flip}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "ghost.txt"), "w") as f:  # Creates ghost.txt
            for ghost in Game.ghosts:  # Loops over ghosts and adds their data
                f.write(f"{ghost.x} {ghost.y} {ghost.type}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "collectable.txt"), "w") as f:  # Creates collectable.txt
            for collectable in Game.collectables:  # Loops over collectables and adds their data
                f.write(f"{collectable.x} {collectable.y}\n")  # Writes to the file

        with open(os.path.join("./game_data/custom", name, "moving_platform.txt"), "w") as f:  # Moving_platform.txt
            for platform in Game.moving_platforms:  # Loops over collectables and adds their data
                f.write(f"{platform.pos1[0]} {platform.pos1[1]} {platform.pos2[0]} {platform.pos2[1]} "
                        f"{platform.length} {platform.width} {platform.speed}\n")
                # Writes to the file

        with open(os.path.join("./game_data/custom", name, "data.txt"), "w") as f:  # Creates data.txt
            f.write(f"{PacMan.start_pos[0]} {PacMan.start_pos[1]}")  # Adds pacman start position
            f.write("\n0")  # Adds the personal best time

    @staticmethod
    def load(file):  # Loads game data
        # Starts by clearing all previous data
        Game.clear()
        # Each line below loads a specific part of the game data
        GameData.load_file(os.path.join(file, "platform.txt"), Platform, Game.platforms)
        GameData.load_file(os.path.join(file, "bouncy.txt"), Bouncy, Game.platforms)
        GameData.load_file(os.path.join(file, "wall.txt"), Wall, Game.platforms)
        GameData.load_file(os.path.join(file, "jump_through.txt"), JumpThrough, Game.jump_through)
        GameData.load_file(os.path.join(file, "spike.txt"), Spike, Game.spikes)
        GameData.load_file(os.path.join(file, "ghost.txt"), Ghost, Game.ghosts)
        GameData.load_file(os.path.join(file, "collectable.txt"), Collectable, Game.collectables)

        with open(os.path.join(file, "moving_platform.txt"), "r") as f:  # Reads the moving platforms file
            for line in f.readlines():  # Loops over each line of the file
                data = [float(i) for i in line.split()]  # Data is extracted and put into a list using split()
                Game.moving_platforms.append(MovingPlatform((data[0], data[1]), (data[2], data[3]), data[4],
                                                            data[5], data[6]))

        with open(os.path.join(file, "data.txt"), "r") as f:  # reads the data.txt file
            data = [float(i) for i in str(f.readlines()[0]).split()]  # First line is extracted
            Game.pacman.set_pos(*data)  # Pacman spawn is set to the first line of the data.txt file

    @staticmethod
    def update_pb(location, pb):  # Updates the personal best time of a level
        with open(os.path.join("./", location, "data.txt"), "r") as f:  # Reads the data.txt file
            lines = f.readlines()  # Reads each line
            if float(lines[1]) > pb or float(lines[1]) == 0:  # If the new PB was faster it is updated
                lines[1] = str(pb)
        with open(os.path.join("./", location, "data.txt"), "w") as f:  # The file is now re-opened in write mode
            f.writelines(lines)  # The new changes are written to the file

    @staticmethod
    def get_pb(location):  # Returns the current personal best time for a level
        with open(os.path.join("./", location, "data.txt"), "r") as f:  # Reads the data.txt file
            return f.readlines()[1]  # Returns the second line of the file


class Game:  # Responsible for running the game
    # Class variables are defined
    BG = (0, 0, 0)  # Game background
    SCROLL_X = 0  # Game scrolling
    SCROLL_Y = 0
    start_time = datetime.datetime.now()  # Starting time. (Used for the timer)

    pacman = PacMan(Window.LENGTH / 2, Window.WIDTH / 2)  # Pacman is created
    # All platforms, spikes etc are cleared
    spikes = []
    ghosts = []
    moving_platforms = []
    jump_through = []
    platforms = []
    collectables = []

    def __init__(self, level, game_type, number=0):  # Doesn't require anything to initialise
        self.game_type = game_type  # Game type is either normal or custom
        self.number = number
        self.level = level

        self.win = window.win  # This just makes it easier to reference the window

        self.click = False  # Will be set to th x and y of a mouse click
        self.drag = False  # Will be set to true if the user is dragging with the mouse

        self.ground_width = 70  # Width of the ground
        self.ground_spacing = 100  # Spacing between the triangle part of the ground
        self.ground_colour = (255, 0, 0)  # Red
        self.ground_scroll = 0  # The scroll of the ground

        self.score_font = pygame.font.Font("freesansbold.ttf", 40)  # The font used to display the score
        self.text = self.score_font.render("0/0", True, (255, 255, 255))  # The score starts at 0/0 and is white
        PacMan.score = 0  # Resets Pacman's score (the number of collectables eaten)
        self.time = self.score_font.render("0", True, (255, 255, 255))
        Game.start_time = datetime.datetime.now()
        PacMan.time = 0

        self.clock = pygame.time.Clock()  # Clock used to create a max FPS
        self.FPS = 60  # Max FPS is set to 60 frames per second
        self.edit = EditMode()  # Edit-mode class is created

        self.mode = "play"  # The starting game mode is on play
        self.hit_box = False  # Determines whether hit-boxes are shown or hidden

        self.pause_img = pygame.image.load("assets/pause.png")
        self.pause_btn = Button(self.win, self.pause_img, (Window.LENGTH - self.pause_img.get_width() - 10, 10),
                                self.pause)

        Game.clear()  # Clears all game data
        if level:  # If there is data to load
            GameData.load(level)  # Loads game data

        self.run = True
        while self.run:  # Main loop of the application
            self.game_loop()

    def pause(self):  # When the pause button is pressed
        pause_img = pygame.image.load("assets/pause_screen.png")  # The background pause image

        resume_img = pygame.image.load("assets/resume.png")  # The resume image
        resume_btn = Button(self.win, resume_img, (Window.LENGTH/2 - resume_img.get_width()/2, 280), 0)  # Resume button
        if self.game_type == "custom":  # If it is a custom level
            save_img = pygame.image.load("assets/save_quit.png")
            save_btn = Button(self.win, save_img, (Window.LENGTH/2 - save_img.get_width()/2, 500), 0)  # Save button
            no_save_img = pygame.image.load("assets/don't_save.png")  # Don't save button
            no_save_btn = Button(self.win, no_save_img, (Window.LENGTH/2 - no_save_img.get_width()/2, 400), 0)
        else:
            quit_img = pygame.image.load("assets/quit2.png")  # Quit button image
            quit_btn = Button(self.win, quit_img, (Window.LENGTH/2 - quit_img.get_width()/2, 400), 0)  # Quit button

        run = True
        while run:  # The main loop while the game is paused
            for event in pygame.event.get():  # Loops over all events
                if event.type == pygame.KEYDOWN:  # Checks for a key press event
                    if event.key == pygame.K_ESCAPE:  # Escape = quit
                        if self.game_type == "normal":  # If it is a built in level
                            run = False  # Pause screen is simply closed
                            self.run = False
                        else:
                            GameData.save(self.level)  # Game is saved
                            self.run = False
                            run = False
            self.win.blit(pause_img, (Window.LENGTH / 2 - pause_img.get_width() / 2, Window.WIDTH / 2 -
                                      pause_img.get_height() / 2))  # Pause image is drawn in the centre

            self.time = self.score_font.render(
                str(round((datetime.datetime.now() - Game.start_time).total_seconds(), 2)),
                True, (255, 255, 255))  # The current time is updated
            # Estimated length of the time box
            length = 25 * (len(str(int((datetime.datetime.now() - Game.start_time).total_seconds()))) + 2) + 10
            pygame.draw.rect(self.win, Game.BG, (4, 4, length, self.time.get_height() + 2))  # Black box is drawn
            pygame.draw.rect(self.win, (0, 255, 0), (2, 2, length + 4, self.time.get_height() + 4), 3)  # Green outline
            self.win.blit(self.time, (5, 5))  # Current time is displayed on screen

            mouse = pygame.mouse.get_pos()  # Gets mouse position
            pressed = pygame.mouse.get_pressed(3)[0]  # If left click
            if resume_btn.update(mouse, pressed):
                run = False  # If resume is pressed the loop is ended
            if self.game_type == "custom":
                if save_btn.update(mouse, pressed):  # If the save button is pressed
                    GameData.save(self.level)  # Level is saved
                    self.run = False  # Quits the pause screen and closes the game
                    run = False
                if no_save_btn.update(mouse, pressed):  # If the don't save button is pressed
                    self.run = False  # Quits the pause screen and closes the game
                    run = False
            else:
                if quit_btn.update(mouse, pressed):  # If the quit button is pressed
                    self.run = False  # Quits the pause screen and closes the game
                    run = False

            pygame.display.update()  # Screen is updated

    def render_screen(self):  # Renders everything on the screen
        self.win.fill(Game.BG)  # Fills the screen black

        # Draws the ground
        pygame.draw.line(self.win, self.ground_colour, (0, Window.WIDTH - 65 - Game.SCROLL_Y),
                         (Window.LENGTH, Window.WIDTH - 65 - Game.SCROLL_Y), 12)  # Bottom and top red lines
        pygame.draw.line(self.win, self.ground_colour, (0, Window.WIDTH - 77 - Game.SCROLL_Y + self.ground_width),
                         (Window.LENGTH, Window.WIDTH - 77 - Game.SCROLL_Y + self.ground_width), 12)
        for i in range(-1, int(Window.LENGTH / self.ground_spacing) + 2):  # Draws the left side of the triangles
            pygame.draw.line(self.win, self.ground_colour, (i * self.ground_spacing - self.ground_scroll, Window.WIDTH -
                                                            77 - Game.SCROLL_Y + self.ground_width),
                             (i * self.ground_spacing + self.ground_spacing / 2 - self.ground_scroll, Window.WIDTH - 65
                              - Game.SCROLL_Y), 15)
        for i in range(-1, int(Window.LENGTH / self.ground_spacing) + 2):  # Draws the right side of the triangles
            pygame.draw.line(self.win, self.ground_colour, (i * self.ground_spacing + self.ground_spacing / 2 -
                                                            self.ground_scroll, Window.WIDTH - 65 - Game.SCROLL_Y),
                             ((i + 1) * self.ground_spacing - self.ground_scroll, Window.WIDTH - 77 - Game.SCROLL_Y +
                              self.ground_width), 15)

        self.ground_scroll = Game.SCROLL_X  # The ground scroll is set to the game scroll
        if self.ground_scroll >= self.ground_spacing or self.ground_scroll < -self.ground_spacing:  # Loops back
            self.ground_scroll = Game.SCROLL_X - int((Game.SCROLL_X / self.ground_spacing)) * self.ground_spacing

        for platform in Game.platforms:  # Draws platforms
            platform.draw(self.win, hit_box=self.hit_box)
        for danger in Game.spikes:  # Draws spikes
            danger.draw(self.win, hit_box=self.hit_box)
        for platform in Game.jump_through:  # Draws jump through platforms
            platform.draw(self.win, hit_box=self.hit_box)
        for collectable in Game.collectables:  # Draws collectables
            collectable.draw(self.win, hit_box=self.hit_box, edit=self.game_type == "custom")
        for platform in Game.moving_platforms:  # Draws moving platforms
            if self.mode == "edit":
                platform.draw_path(self.win, hit_box=self.hit_box)
            else:
                platform.draw(self.win, hit_box=self.hit_box)
        for ghost in Game.ghosts:  # Draws ghosts
            ghost.draw(self.win, hit_box=self.hit_box)

        Game.pacman.draw(self.win, hit_box=self.hit_box)  # Draws pacman

        # Score text is updated and drawn in the top left corner
        self.text = self.score_font.render(f"{PacMan.score}/{len(Game.collectables)}", True, (255, 255, 255))
        self.win.blit(self.text, (Window.LENGTH/2 - self.text.get_width()/2, 5))
        # Current time is found
        self.time = self.score_font.render(str(round((datetime.datetime.now() - Game.start_time).total_seconds(), 2)),
                                           True, (255, 255, 255))
        # Estimate for time box length
        length = 25 * (len(str(int((datetime.datetime.now() - Game.start_time).total_seconds()))) + 2) + 10
        pygame.draw.rect(self.win, Game.BG, (4, 4, length, self.time.get_height() + 2))  # Black box is drawn
        pygame.draw.rect(self.win, (0, 255, 0), (2, 2, length + 4, self.time.get_height() + 4), 3)  # Green outline
        self.win.blit(self.time, (5, 5))  # Current time is drawn

    def game_loop(self):  # The main loop for the game class
        if self.mode == "play":  # If mode is play it then updates the scroll x and y
            Game.SCROLL_X += (Game.pacman.x + Game.pacman.r/2 - Game.SCROLL_X - Window.LENGTH / 2) / 15  # 15 delay
            Game.SCROLL_Y += (Game.pacman.y + Game.pacman.r/2 - Game.SCROLL_Y - Window.WIDTH / 2) / 15

        keys = pygame.key.get_pressed()  # Gets all keys
        mouse = pygame.mouse.get_pos()  # Gets mouse position

        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the game is saved and the program closes
                    self.pause()
                if event.key == pygame.K_e and self.game_type == "custom":  # E toggles play and edit mode
                    if self.mode == "play":
                        self.mode = "edit"
                        self.edit.reset()
                    else:
                        self.mode = "play"
                        self.click = False  # Resets the click and drag variables
                        self.drag = False
                if event.key == pygame.K_h:  # H toggles hit-boxes
                    if self.hit_box:
                        self.hit_box = False
                    else:
                        self.hit_box = True
            if event.type == pygame.MOUSEBUTTONDOWN and self.mode == "edit":  # When clicked in edit mode
                if event.button == 1:  # This specifies the button press to be a left click
                    self.click = mouse[0] + self.edit.scroll_x, mouse[1] + self.edit.scroll_y  # Mouse x and y is stored
            if event.type == pygame.MOUSEBUTTONUP and self.mode == "edit":  # When button is released
                if event.button == 1:  # This specifies the button press to be a left click
                    if not self.drag:  # If the user was not dragging then add a platform
                        self.edit.add_platform(mouse[0], mouse[1])  # Uses the edit mode add_platform() method
                    self.click = False  # Resets click and drag variables
                    self.drag = False

        if self.click:  # If user has right clicked. Separates clicks from drags
            if math.dist((mouse[0] + self.edit.scroll_x, mouse[1] + self.edit.scroll_y),
                         (self.click[0], self.click[1])) > 5:  # If dist moved > 5 pixels
                self.edit.drag(self.click, (mouse[0], mouse[1]))  # Drags the screen to the mouse position
                self.drag = True  # This is then considered a drag

        self.render_screen()  # Renders the screen

        if self.mode == "play":  # If in play mode pacman, collectables and ghosts need to update
            Game.pacman.update(keys)  # Pacman is updated
            for ghost in Game.ghosts:
                ghost.update()  # Each ghost is updated

            won = True  # Temporarily set to True
            for collectable in Game.collectables:  # Loops over collectables
                collectable.update()  # Each one is updated
                if not collectable.eaten:  # If any collectable is not eaten then won is set to False
                    won = False
            if won and self.game_type == "normal":  # If you have won
                self.level_beaten()  # Level beaten screen
                self.run = False  # Game is quit
        else:  # Otherwise an edit mode update is called
            self.edit.update(keys, self.win)
        self.pause_btn.update(mouse, pygame.mouse.get_pressed(3)[0])  # Updates the pause button

        pygame.display.update()  # Display is updated
        self.clock.tick(self.FPS)  # clock is used to cap FPS

    def level_beaten(self):  # Called when a level has been beaten
        height = 0  # Height of a gray screen
        font = pygame.font.Font("freesansbold.ttf", 64)  # Level beaten font
        text = font.render("Level Beaten", True, (255, 255, 255))  # Drawn in white
        time = round((datetime.datetime.now() - Game.start_time).total_seconds(), 2)  # Final time is calculated
        time_text = font.render(f"Time: {time}", True, (255, 255, 255))  # Drawn in white

        GameData.update_pb(self.level, time)  # New potential PB is updated

        global progress
        if self.number > progress:  # If this level has not already been completed
            with open("game_data/progress.txt", "w") as f:  # Loads progress from the progress text file
                f.truncate()  # Empties previous information
                f.write(str(self.number))  # New progress is written
            progress = self.number  # Progress variable is updated

        timer = int(2 * self.FPS)  # Repeats for 2 seconds
        for i in range(timer):
            pygame.draw.rect(self.win, (20, 20, 20), (0, 0, Window.LENGTH, height))  # Gray box is drawn

            if height < Window.WIDTH:  # Box increases in width
                height += 20
            else:  # Once full size the text appears
                self.win.blit(text,
                              (Window.LENGTH / 2 - text.get_width() / 2, Window.WIDTH / 2 - text.get_height() / 2))
                self.win.blit(time_text, (Window.LENGTH / 2 - time_text.get_width() / 2, Window.WIDTH / 2 +
                                          text.get_height() / 2 + 50))

            pygame.display.update()  # Screen is updated
            self.clock.tick(self.FPS)  # Caps FPS

    @staticmethod
    def clear():  # Clears all objects
        Game.pacman = PacMan(Window.LENGTH / 2, Window.WIDTH / 2)  # Pacman is created
        Game.SCROLL_X = 0  # Scroll x and y is reset
        Game.SCROLL_Y = 0
        Game.platforms = []  # All lists are reset
        Game.jump_through = []
        Game.spikes = []
        Game.ghosts = []
        Game.collectables = []
        Game.moving_platforms = []


class CreditScreen:  # Responsible for the credits screen
    def __init__(self):  # Initialises the credit screen
        self.win = window.win  # window
        self.credits_img = pygame.image.load("assets/credits.png")  # Credits background image

        self.back_btn = Button(self.win, pygame.image.load("assets/back.png"), (10, 10), self.quit)  # Back button class

        self.run = True
        while self.run:  # Main loop
            self.game_loop()

    def quit(self):  # If quit run is set to False
        self.run = False

    def game_loop(self):  # Main loop of the credits screen
        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the program closes
                    self.run = False  # This will return the user to the home screen

        mouse = pygame.mouse.get_pos()  # Mouse position
        pressed = pygame.mouse.get_pressed(3)  # If the mouse is pressed

        self.win.fill((0, 0, 0))  # Window is filled black
        self.win.blit(self.credits_img, ((Window.LENGTH / 2) - (self.credits_img.get_width() / 2), 0))  # BG is drawn
        self.back_btn.update(mouse, pressed[0])  # Back button is updated
        pygame.display.update()  # Screen is updated


class StoryLine:  # Responsible for the storyline screen
    def __init__(self):
        self.win = window.win  # Window
        self.bg = pygame.image.load("assets/stoyline_bg.png")  # Background is loaded

        self.back_btn = Button(self.win, pygame.image.load("assets/back.png"), (10, 10), self.quit)  # Back button class

        self.run = True
        while self.run:  # Main loop
            self.game_loop()

    def quit(self):  # If the game is quit run is set to False
        self.run = False

    def game_loop(self):
        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the program closes
                    self.run = False  # This will return the user to the home screen

        mouse = pygame.mouse.get_pos()  # Gets mouse position
        pressed = pygame.mouse.get_pressed(3)  # If the mouse has been pressed

        self.win.fill((0, 0, 0))  # Fills the screen black
        self.win.blit(self.bg, ((Window.LENGTH / 2) - (self.bg.get_width() / 2), 0))  # Background is drawn
        self.back_btn.update(mouse, pressed[0])  # Back button is updated
        pygame.display.update()  # Screen is updated


class HelpScreen:  # Responsible for the help screen page
    def __init__(self):  # Initialises the help screen
        self.win = window.win  # Window
        self.img_0 = pygame.image.load("assets/how_to_play_0.png")  # Page 1
        self.img_1 = pygame.image.load("assets/how_to_play_1.png")  # Page 2
        self.current_img = 0  # Current image is 0

        btn_img = pygame.image.load("assets/arrow.png")  # Left and right button image is loaded
        self.left_btn = Button(self.win, btn_img, (70, Window.WIDTH / 2 - (btn_img.get_height() / 2)), self.next_img)
        self.right_btn = Button(self.win, pygame.transform.flip(btn_img, True, False),
                                (Window.LENGTH - btn_img.get_width() - 70, Window.WIDTH / 2 -
                                 (btn_img.get_height() / 2)), self.next_img)  # Buttons are made
        self.back_btn = Button(self.win, pygame.image.load("assets/back.png"), (10, 10), self.quit)  # Back button class

        self.run = True
        while self.run:  # Main loop
            self.game_loop()

    def next_img(self):  # Cycles to the next image
        self.current_img += 1  # Image is increased by 1
        if self.current_img > 1:
            self.current_img = 0  # Resets to 0

    def quit(self):  # If quit is called it will return to the home page
        self.run = False

    def game_loop(self):  # Main loop of the help screen
        mouse = pygame.mouse.get_pos()  # Gets mouse position
        pressed = pygame.mouse.get_pressed(3)  # If the mouse has been pressed
        self.win.fill((0, 0, 0))  # Fills the screen black

        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the program closes
                    self.run = False  # This will return the user to the home screen
            if event.type == pygame.MOUSEBUTTONDOWN:  # Mouse press
                if event.button == 1:  # Left click
                    self.left_btn.update(mouse, True)  # Left and Rick buttons are updated
                    self.right_btn.update(mouse, True)

        self.left_btn.update(mouse, False)  # Left and Right buttons are updated
        self.right_btn.update(mouse, False)

        if self.current_img == 0:  # Correct image is drawn
            self.win.blit(self.img_0, ((Window.LENGTH / 2) - (self.img_0.get_width() / 2), 0))
        else:
            self.win.blit(self.img_1, ((Window.LENGTH / 2) - (self.img_0.get_width() / 2), 0))

        self.back_btn.update(mouse, pressed[0])  # Back button is updated
        pygame.display.update()  # Display is updated


class LevelSelect:  # Responsible for the leve select screen (both main and custom levels).
    def __init__(self):  # Initialises the screen
        self.win = window.win  # Window
        self.mode = "main"  # Either main or custom
        self.enable_buttons = False  # Buttons start disabled (this was to fix a glitch).

        self.back_btn = Button(self.win, pygame.image.load("assets/back.png"), (10, 10), self.quit)  # Back button
        self.title = pygame.image.load("assets/level_select.png")  # Title image

        main_btn_img = pygame.image.load("assets/main.png")  # Main button image
        self.main_btn = Button(self.win, main_btn_img, (100, 130), lambda: self.change_mode("main"), select=True)
        custom_btn_img = pygame.image.load("assets/custom.png")  # Custom button image
        self.custom_btn = Button(self.win, custom_btn_img, (Window.LENGTH - 60 - custom_btn_img.get_width(), 130),
                                 lambda: self.change_mode("custom"), select=True)
        self.main_btn.disable = True  # Main button is initially disabled

        self.page_pause = 30  # Delay while cycling through pages
        self.page = 0  # Start page is 0
        btn_img = pygame.image.load("assets/arrow.png")  # Used for left and right arrows
        self.left_btn = Button(self.win, btn_img, (70, 420), lambda: self.change_page(-1))  # Left arrow
        self.right_btn = Button(self.win, pygame.transform.flip(btn_img, True, False),
                                (Window.LENGTH - btn_img.get_width() - 70, 420), lambda: self.change_page(1))  # right

        number = len(os.listdir("game_data/built_in"))  # Number of built-in items
        self.main_buttons = [[LevelBtn(self.win, x*200 + 165, 250 + (y % 2)*250, "main", 0, num=y*5+x+1)
                              for x in range(5)] for y in range(number // 5)]  # Loads built in buttons
        self.main_buttons.append([LevelBtn(self.win, x*200 + 165, 250 + ((number // 5) % 2)*250, "main", 0,
                                           num=(number // 5)*5+x+1) for x in range(number % 5)])  # Loads buttons
        self.main_number = number  # Number of buttons

        files = os.listdir("game_data/custom")
        number = len(files)  # Number of custom items
        # Loads buttons
        self.custom_buttons = [[LevelBtn(self.win, x*200 + 165, 250 + (y % 2)*250, "custom", self.delete,
                                         name=files[y*5+x]) for x in range(5)] for y in range(number // 5)]
        self.custom_buttons.append([LevelBtn(self.win, x*200 + 165, 250 + ((number // 5) % 2)*250, "custom",
                                             self.delete, name=files[(number // 5)*5+x]) for x in range(number % 5)])
        self.custom_number = number  # Number of buttons

        img = pygame.image.load("assets/add.png")  # Add button image
        self.add_btn = Button(self.win, img, ((number % 5)*200 + 190, 270 + ((number // 5) % 2)*250), self.new_custom)

        self.run = True
        while self.run:  # Main loop of the level select screen
            self.game_loop()

    def quit(self):  # Called when the escape key or back button is pressed
        self.run = False

    def delete(self, location):  # Deletes a certain level
        shutil.rmtree(os.path.join("./game_data/custom", location))  # Will remove the folder at the given location
        self.reload()  # All levels are reloaded

    def reload(self):
        files = os.listdir("game_data/custom")
        number = len(files)  # Number of custom items
        self.custom_buttons = [[LevelBtn(self.win, x*200 + 165, 250 + (y % 2)*250, "custom", self.delete,
                                         name=files[y*5+x]) for x in range(5)] for y in range(number // 5)]  # Buttons
        self.custom_buttons.append([LevelBtn(self.win, x*200 + 165, 250 + ((number // 5) % 2)*250, "custom",
                                             self.delete, name=files[(number // 5)*5+x]) for x in range(number % 5)])
        self.custom_number = number  # Saves number of buttons
        self.add_btn.move(((number % 5) * 200 + 190, 270 + ((number // 5) % 2) * 250))  # Add button is moved

    def new_custom(self):  # A new custom level is made
        Game("", "custom")
        self.reload()  # Levels are reloaded

    def change_page(self, x):  # Page is changed by the value of x
        if not self.page_pause > 0:  # Page pause prevents pages swapping too fast
            self.page_pause = 30  # Page pause is set back to 30
            self.page += x  # Page is changed

    def change_mode(self, mode):  # Mode is changed. Either custom --> main or main --> custom
        self.mode = mode
        self.page = 0  # Page is reset
        if mode == "main":  # If it should be changed to main
            self.custom_btn.disable = False  # Disable custom button
            self.main_btn.disable = True  # Enable main button
        else:  # If it should be changed to custom
            self.custom_btn.disable = True  # Disable main button
            self.main_btn.disable = False  # Enable custom button

    def render_lvl_btn(self, mouse, pressed):  # Renders the level buttons
        if self.mode == "main":  # If it is on the main page
            for row in self.main_buttons[self.page * 2:self.page * 2 + 2]:  # Loops over all buttons
                for item in row:
                    item.update(mouse, pressed)  # Buttons are drawn and updated
        else:  # If it is on the custom page
            if self.page == self.custom_number // 10:
                self.add_btn.update(mouse, pressed)  # Add button is drawn and updated
            for row in self.custom_buttons[self.page * 2:self.page * 2 + 2]:  # Loops over all buttons
                for item in row:
                    item.update(mouse, pressed)  # Buttons are drawn and updated

    def game_loop(self):  # Main loop of the level select screen
        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the program closes
                    self.run = False  # This will return the user to the home screen

        mouse = pygame.mouse.get_pos()  # Gets mouse position
        pressed = pygame.mouse.get_pressed(3)  # If mouse pressed

        self.win.fill((0, 0, 0))  # Screen is filled black
        self.win.blit(self.title, (Window.LENGTH / 2 - self.title.get_width() / 2, 10))  # Title is drawn
        # Each button is updated
        self.back_btn.update(mouse, pressed[0])
        self.main_btn.update(mouse, pressed[0])
        self.custom_btn.update(mouse, pressed[0])

        if self.page > 0:
            self.left_btn.update(mouse, pressed[0])  # Left arrow is drawn
        if self.mode == "main":
            if self.page < (self.main_number // 10):
                self.right_btn.update(mouse, pressed[0])  # Right arrow is drawn
        else:
            if self.page < (self.custom_number // 10):
                self.right_btn.update(mouse, pressed[0])  # Right arrow is drawn

        if self.enable_buttons:  # If buttons are enabled
            self.render_lvl_btn(mouse, pressed[0])  # Buttons are drawn
        else:
            self.enable_buttons = not pressed[0]  # If the mouse is not pressed buttons are then enabled

        pygame.display.update()  # Display is updated
        if self.page_pause > 0:
            self.page_pause -= 1  # Page pause is decreased


class HomeScreen:  # Responsible for the home screen of the game
    def __init__(self):  # Initialises the home screen
        self.win = window.win  # Window

        play_btn_image = pygame.image.load("assets/play_btn.png")  # PLay button image
        self.play_btn = Button(self.win, play_btn_image, ((Window.LENGTH / 2) - (play_btn_image.get_width() / 2), 230),
                               lambda: self.button_pressed("play"))
        how_btn_image = pygame.image.load("assets/how_to_play_btn.png")  # How to play button image
        self.how_btn = Button(self.win, how_btn_image, ((Window.LENGTH / 2) - (how_btn_image.get_width() / 2), 400),
                              lambda: self.button_pressed("help"))
        credits_btn_image = pygame.image.load("assets/credits_btn.png")  # Credits button image
        self.credits_btn = Button(self.win, credits_btn_image,
                                  ((Window.LENGTH / 2) - (credits_btn_image.get_width() / 2), 550),
                                  lambda: self.button_pressed("credits"))
        quit_btn_image = pygame.image.load("assets/quit.png")  # Quit button image
        self.quit_btn = Button(self.win, quit_btn_image, (10, Window.WIDTH - quit_btn_image.get_height()),
                               lambda: self.button_pressed("quit"))
        storyline_btn_img = pygame.image.load("assets/storyline_btn.png")  # Storyline button image
        self.storyline_btn = Button(self.win, storyline_btn_img, (Window.LENGTH - storyline_btn_img.get_width() - 10,
                                                                  Window.WIDTH - storyline_btn_img.get_height()),
                                    lambda: self.button_pressed("storyline"))

        self.title_img = pygame.image.load("assets/title.png")  # Title image
        self.ghosts = [FallingGhost(self.win) for _ in range(40)]  # Falling ghosts are created in a list

        self.clock = pygame.time.Clock()  # Clock is initialised

        self.run = True
        while self.run:  # Main loop of the home screen
            self.game_loop()

    def button_pressed(self, btn):  # If any button has been pressed
        if btn == "play":
            LevelSelect()  # Play starts the level select
        if btn == "credits":
            CreditScreen()  # Credits starts the credits screen
        if btn == "help":
            HelpScreen()  # Help starts the help screen
        if btn == "quit":
            self.run = False  # Quits the game
        if btn == "storyline":
            StoryLine()  # Storyline starts the storyline screen

    def game_loop(self):
        for event in pygame.event.get():  # Loops over all events
            if event.type == pygame.KEYDOWN:  # Checks for a key press event
                if event.key == pygame.K_ESCAPE:  # If escape key is pressed the program closes
                    pygame.quit()  # Quits the game
                    quit()

        mouse = pygame.mouse.get_pos()  # Gets mouse position
        pressed = pygame.mouse.get_pressed(3)  # If mouse is pressed

        self.win.fill((0, 0, 0))  # Screen is filled black

        for ghost in self.ghosts:  # Each of the falling ghosts are drawn
            ghost.draw()
        # Every button is drawn
        self.play_btn.update(mouse, pressed[0])
        self.how_btn.update(mouse, pressed[0])
        self.credits_btn.update(mouse, pressed[0])
        self.quit_btn.update(mouse, pressed[0])
        self.storyline_btn.update(mouse, pressed[0])

        self.win.blit(self.title_img, ((Window.LENGTH / 2) - (self.title_img.get_width() / 2), 30))  # Title is drawn

        pygame.display.update()  # Screen is updated
        self.clock.tick(50)  # Clock is used to cap FPS


if __name__ == '__main__':  # Will run at the beginning of the program
    pygame.mixer.init()  # Initializes pygame's mixer used for sound
    pygame.mixer.music.load("sounds/Dance_of_the_Pixies.mp3")  # Loads the background music
    pygame.mixer.music.play(-1)  # Plays music infinitely

    window = Window()  # Window is initialised
    HomeScreen()  # Home screen is started

    pygame.mixer.stop()  # Sounds are stopped
