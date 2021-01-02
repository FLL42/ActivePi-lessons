# Import modules.
import time, math, threading, random
from threading import Event
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont # sudo apt install python3-pil
import adafruit_ssd1306 # sudo pip3 install adafruit-circuitpython-ssd1306
import adafruit_mpu6050 # sudo pip3 install adafruit-circuitpython-mpu6050
from adafruit_extended_bus import ExtendedI2C as I2C # sudo pip3 install adafruit-extended-bus
from enum import Enum # An enum is a way to use names instead of numbers, basically. We are using enums to identify the type of obstacle and the type of jump.

## This program uses Adafruit's libraries to run CircuitPython on Raspberry Pi -- there are multiple ways to control GPIO pins/I2C and this is one of them.

# This is a dictionary of bitmaps (so just arrays of image data) to display.
bitmaps = {}

# Ground bitmap: the floor. (width = 128, height = 5)
bitmaps["ground"] = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]]

# Small cactus bitmap (width = 5, height = 10)
bitmaps["small_cactus"] = [[0, 0, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 1], [1, 0, 1, 0, 1], [1, 0, 1, 0, 1], [1, 0, 1, 1, 0], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0], [0, 0, 1, 0, 0]]

# Wide cactus bitmap (width = 17, height = 15)
bitmaps["wide_cactus"] = [[0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1]]

# Tall cactus bitmap (width = 7, height = 18)
bitmaps["tall_cactus"] = [[0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 0, 0], [1, 0, 0, 1, 0, 0, 1], [1, 0, 0, 1, 0, 0, 1], [0, 1, 0, 1, 0, 0, 1], [0, 0, 1, 1, 0, 0, 1], [0, 0, 0, 1, 0, 0, 1], [0, 1, 0, 1, 0, 1, 1], [0, 1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 1, 0, 0], [0, 1, 0, 1, 0, 0, 0], [0, 1, 0, 1, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0, 0]]

# Dinosaur bitmap (width = 10, height = 11)
bitmaps["dino"] = [[0, 0, 0, 0, 0, 1, 1, 1, 1, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 0, 1, 1, 1], [1, 0, 0, 0, 1, 1, 1, 1, 1, 0], [1, 1, 0, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [0, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 1, 0, 1, 1, 0, 0, 0]]

## Running animation:
# Dinosaur running, bitmap 1 (width = 10, height = 11)
bitmaps["dino_run_1"] = [[0, 0, 0, 0, 0, 1, 1, 1, 1, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 0, 1, 1, 1], [1, 0, 0, 0, 1, 1, 1, 1, 1, 0], [1, 1, 0, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [0, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 0, 0, 1, 1, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0, 0, 0]]

# Dinosaur running, bitmap 2 (width = 10, height = 11)
bitmaps["dino_run_2"] = [[0, 0, 0, 0, 0, 1, 1, 1, 1, 0], [0, 0, 0, 0, 1, 1, 1, 1, 1, 1], [0, 0, 0, 0, 1, 1, 0, 1, 1, 1], [1, 0, 0, 0, 1, 1, 1, 1, 1, 0], [1, 1, 0, 1, 1, 1, 1, 1, 0, 0], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1, 1, 0, 1], [0, 1, 1, 1, 1, 1, 1, 0, 0, 0], [0, 0, 1, 0, 0, 1, 0, 0, 0, 0], [0, 0, 1, 1, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 1, 0, 0, 0]]

### DEBUGGING FOR BITMAPS ###
def print_bitmap(bmp):
    """
    This function prints out a bitmap to the console -- good for testing.
    """
    for i in bmp:
        for a in i:
            print("\u2588" if a == 1 else " ", end="")
        print()

def create_bitmap(filename, width, height):
    im = Image.open(filename)
    arr = im.getdata()
    array = []
    for data in arr:
        if data:
            array.append(0)
        else:
            array.append(1)

    bitmap = []
    for i in range(height):
        row = []
        for i2 in range(width):
            row.append(array[i * width + i2])
        bitmap.append(row)
    print_bitmap(bitmap)
    return bitmap
###    END OF DEBUGGING   ###

def call_repeatedly(interval, function, *args):
    """
    Helper function to continuously run a function in the background (on a separate thread).
    """
    is_stopped = Event() # an Event has a function to wait until a flag is true or until a timeout is hit.
    # This makes it very useful for us because the loop can be stopped by setting the flag to True,
    # and if the flag isn't True, we can just wait. For more info, see here:
    # https://docs.python.org/3/library/threading.html#threading.Event
    def loop():
        while not stopped.wait(interval): # wait until the interval has passed or until the flag has been set
            function(*args) # once one of those things has happened, call the function with the provided arguments
    Thread(target=loop).start() # start the loop in the background,    
    return stopped.set # and return the function to call to set the flag (described above)

# Create class for the game that has variables for the display and other things critical to the game.
class Game:
    def __init__(self, min_speed = 10, max_speed = 26):
        # Create I2C interfaces.
        self.i2c_display = busio.I2C(SCL, SDA)
        self.i2c_accel = I2C(3) # GPIO23 = SDA, GPIO24 = SCL -- enable the i2c-gpio overlay!

        # Update minimum and maximum speeds (in pixels / second)
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.current_speed = min_speed # to start

        # Create list of obstacles (empty to start)
        self.obstacles = []

        # Create a variable to hold the score
        self.score = 0

        # Create a dino 🦖
        self.dino = Dino()

        # The PiOLED is 128 pixels x 32 pixels, and communicates over I2C, so we need to give it the I2C interface created above.
        self.display = adafruit_ssd1306.SSD1306_I2C(128, 32, self.i2c_display)

        # Initialize the accelerometer.
        self.accelerometer = adafruit_mpu6050.MPU6050(self.i2c_accel)

        # Get display width & height.
        self.width = display.width
        self.height = display.height

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        # 1-bit color means the only options are full brightness (fill=255) or off (fill=0) -- this display is monochrome.
        self.image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, width, height), outline=0, fill=0)

        # Draw a line at the bottom of the screen (height = 31 & width = 127 because they start at 0, so we are drawing from (0, 31) to (128, 31)).
        # This is the ground for the dino game. The line also is at full brightness (fill=255), 3 pixels high (width=3), and has curved edges (joint="curve").
        # self.draw.line([(0, height), (width, height)], fill=255, width=3, joint="curve")

        # Draw the ground for the dino game (see where we make the bitmap on line 18). Fill = white (255). TODO get final line #
        self.draw.bitmap((0, 27), bitmaps["ground"], fill=255)

        # Update display. (not the obstacles because we haven't started yet)
        self.update_display()

        # Start the game! Call the update() function every 0.05 seconds.
        # This returns a function that will stop the loop.
        self.stop = call_repeatedly(0.05, self.update)

    def update_display(self):
        """
        Updates the display.
        """
        display.image(image)
        display.show()

    def detect_collision(self):
        """
        Detects if there was a collision between the dino and an obstacle.

        Returns if there was a collision or not (if the game ended or not).
        """
        dino_bounding_box = [(18, self.dino.jumping.value), (18 + 10, self.dino.jumping.value + 11)]
        dino_pixels = []
        for y in range(dino_bounding_box[0][1], dino_bounding_box[1][1] + 1):
            for x in range(dino_bounding_box[0][0], dino_bounding_box[1][0] + 1):
                dino_pixels.append((x, y))
        for obstacle in self.obstacles:
            obstacle_top_left = (obstacle.position, 27 - obstacle.obstacle_type.value[1])
            obstacle_bitmap = obstacle.obstacle_type.value[3]
            obstacle_pixels = []
            # Make list of pixels (coordinates) that are obstacles (so only the cactus, not the bounding box)
            for y in range(len(obstacle_bitmap)):
                for x in range(len(obstacle_bitmap[0])):
                    if obstacle_bitmap[y][x] == 1:
                        obstacle_pixels.append((obstacle_top_left[0] + x), (obstacle_top_left[1] + y))
            if len(set(dino_pixels).intersection(obstacle_pixels)) > 0:
                # If there is at least one set of coordinates overlapping the dino and the obstacle,
                # game over!
                print("game over!")
                self.stop()
                return True
        return False


    def update(self):
        """
        Redraws the game's obstacles (if necessary), updates the dino, and updates the display.
        Called in the background, and then again 0.01 seconds after it finishes, and so on in a loop (see the end of __init__).
        """
        self.dino.update()
        for obstacle in self.obstacles:
            obstacle.update()
        self.update_display()

class ObstacleType(Enum):
    """
    Enum for the different obstacle types (small, tall, and wide).

    The raw values are tuples in the format (obstacle_width, obstacle_height, bitmap).
    """
    SMALL = (5, 10, bitmaps["small_cactus"])
    TALL = (7, 18, bitmaps["tall_cactus"])
    WIDE = (17, 15, bitmaps["wide_cactus"])

class Obstacle:
    """
    A class to represent an obstacle.
    """

    def __init__(self, game: Game, obstacle_type = ObstacleType.SMALL):
        self.position = 127 - (obstacle_type.value[0] // 2) # position (x axis only) on the screen. This is the left of the obstacle (hence the - (width // 2) -- // means integer division, so 17 // 2 = 8 rather than 8.5)
        self.obstacle_type = obstacle_type # Type of obstacle
        self.game = game # Variable to hold the game (so we can edit the display)
        self.last_update_time = 0 # The last time we updated the obstacle -- starts at 0, but will be updated to time.time() (current Unix time) when we call update()
    
    def update(self):
        if (time.time() - self.last_update_time) >= (1.0 / self.game.current_speed): # if the time passed since we last updated the obstacle is >= than 1 second divided by the game's current speed (in pixels per second to move the obstacle), then:
            self.game.draw.rectangle([(self.position, 27 - self.obstacle_type.value[1]), (self.position + self.obstacle_type.value[0] + 1, 27 + 1)], fill=0) # Erase the current obstacle so we can redraw it -- "the second point is just outside the drawn rectangle"
            # according to the documentation: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#PIL.ImageDraw.ImageDraw.rectangle
            self.position -= 1 # move the obstacle one pixel to the left
            if self.position == 0: # if the obstacle's position is 0 (all the way to the left),
                self.game.obstacles.remove(self) # remove it from the list of obstacles
            self.game.draw.bitmap((self.position, 27 - self.obstacle_type.value[1]), self.obstacle_type.value[3], fill=255) # Redraw the obstacle @ x = position, y = (27 (which is the top of the ground -- y = 0 is the top of the display) - the obstacle's height).
            self.last_update_time = time.time() # update the last updated time
            if not self.game.detect_collision():
                self.game.score += 1 # Increase the score by 1

class JumpType(Enum): # An enum is basically a way to assign names to values.
    # Now we can use JumpType.HIGH and JumpType.LOW instead of some arbitrary variables.
    # The raw values are the height at which to draw the dino -- located at the top of the dino. (bottom of screen = 31, bottom of ground = 27, bottom of ground - height of dino = 16)
    LOW = 22
    HIGH = 30
    NONE = 16

class Dino:
    """
    Class for the dino 🦖
    """
    def __init__(self, game: Game):
        self.jumping = JumpType.NONE # Is the dino jumping? To start, no.
        self.game = game
        self.velocity = 0 # Relative to the last time self.jumping was JumpType.NONE -- in meters / second.
        self.jump_height = 0 # Relative to the last time self.jumping was JumpType.NONE -- in meters.
        self.last_measured_velocity = time.time_ns() / 1000000000 # in nanoseconds to be more accurate -- divided by 1 billion to get seconds.
        self.bitmap = "1" # whether the bitmap drawn is dino_run_1 or dino_run_2

    def get_jump_height(self):
        """
        Yay calculus!
        """
        # To get velocity (speed) at a particular time, we use the equation velocity = initial_velocity + acceleration * time.
        # To get position from velocity, we use the equation position = velocity * time.
        # Every time we call this function, initial velocity = self.velocity (last measured velocity)
        # so we can keep track of velocity over time.
        # A little bit of error can introduce a LOT of error over time with this equation,
        # which is why we will reset velocity & jump_height to 0 every time self.jumping
        # = JumpType.NONE.
        acceleration = self.game.accelerometer.acceleration # (X, Y, Z) in m/s^2 (how velocity changes over time)
        # Get the current time.
        t = time.time_ns() / 1000000000
        # Recalculate velocity.
        # acceleration[3] is the Z axis acceleration. +9.8 m/s^2 to adjust for gravity.
        # Please change 9.8 to 1.62 if you are using the ActivePi on the moon.
        # Or 3.711 if you're on Mars.
        self.velocity = self.velocity + (acceleration[3] + 9.8) * (t - self.last_measured_velocity)
        # Now calculate the jump height!
        self.jump_height = self.jump_height + self.velocity * (t - self.last_measured_velocity)
        # Finally, update the time last measured to `t`.
        self.last_measured_velocity = t

    def update(self):
        """
        Updates what jumping state we are in (from the accelerometer) and redraws the dino accordingly.
        """
        # acceleration = self.game.accelerometer.acceleration # (X, Y, Z) in m/s^2
        # if acceleration[3] > 8: # https://www.quora.com/How-much-force-in-Newtons-on-average-does-someone-exert-when-they-jump says a high jump is 19.8 m/s^2 of acceleration. -9.8 m/s^2 from gravity and you get 10 m/s^2, so >8 should be a high jump. TODO test with real device so I can get values for me
        #     self.jumping = JumpType.HIGH
        # elif acceleration[3] > -1.8: # > 10 m/s^2 (-9.8 m/s/s for gravity)
        #     self.jumping = JumpType.LOW
        # elif acceleration[3] < -5: # if acceleration < -4.8 m/s/s, the person is not jumping. TODO maybe change this to velocity later (separate thread constantly measuring velocity using V = Vsub0 + at)
        #     self.jumping = JumpType.NONE
        self.game.draw.rectangle([(18, self.jumping.value), (18 + 10 + 1, self.jumping.value + 11 + 1)], fill=0) # Erase the old dino
        self.get_jump_height() # Update our jump height
        if self.jump_height >= 0.3: # High jump >= 0.3 meters (about 1 foot)
            self.jumping = JumpType.HIGH
        elif self.jump_height >= 0.1: # Low jump >= 0.1 meters (about 4 inches)
            self.jumping = JumpType.LOW
        elif self.velocity <= 0: # No jump -- velocity is less than or equal to 0
            self.jumping = JumpType.NONE
            # Also reset velocity + jump height
            self.velocity = 0
            self.jump_height = 0
        self.game.draw.bitmap((18, self.jumping.value), bitmaps["dino_run_"+self.bitmap], fill=255) # Draw the dino at x=18, y=JumpType raw value
        # Change which bitmap we are drawing for the next draw to animate.
        self.bitmap = "1" if self.bitmap == "2" else "2"
        # https://electronics.stackexchange.com/questions/112421/measuring-speed-with-3axis-accelerometer

# Detect jumping -- while acceleration on the Z axis is going up (or more + than normal gravity), you are jumping.
# When acceleration goes back down, not jumping anymore.