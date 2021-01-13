#https://docs.google.com/document/d/1GRzY3Ll2JtlGXUPw1XQmhMr6sUkBdZnunfvKTPCG4-4/edit#
import time 
import board 
import busio
import adafruit_mpu6050
from adafruit_extended_bus import ExtendedI2C as I2C # sudo pip3 install adafruit-extended-bus
import math
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
 
i2c = I2C(11) # GPIO23 = SDA, GPIO24 = SCL for this interface
mpu = adafruit_mpu6050.MPU6050(i2c)
i2c_display = busio.I2C(board.SCL, board.SDA)


#this part is going to be setting up the OLED display so you can print the steps onto it. 

display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c_display)

width = display.width
height = display.height

image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)

draw.rectangle((0, 0, width, height), outline=0, fill=0)

font = ImageFont.truetype("Mario-Kart-DS.ttf", size=32)

# These two lines are initializing the connection between the accelerometer and the raspberry pi. 

#the next 3 lines are to print basic values of the accelerometer
#while True:
    #print(f'Gyro X value: {mpu.acceleration.x}') #prints the value of the x gyro
    #time.sleep(1) #delays for 1 second before looping again

# speed = initial speed + acceleration * time (also known as V = V0 + at)
# position = initial position + speed * time
# acceleration of 1 m/s/s (or m/s^2) means that for the 1st second, speed = 1 m/s. 2nd second, speed = 2 m/s. 3rd second, speed = 3 m/s.

steps = 0 #steps

threshold = 2 #this is the amount of acceleration needed to register as a step
steptrue = False #since our code is a while true to award someone a step when they meet the required acceleration,
# the code still loops when the person IS STILL over the threshold to award a step
#so if this is not there, the amount times the function loops while the person is still over the threshold will be how many steps are awarded,
#not just 1 step each time it goes over
#when someone takes a step, they are over the threshold for maybe .2 seconds, then they will get awarded steps of the number of times the loop runs in .2 seconds. 
#if the bool is there, it awards only one step
normal = 12 # normal value

while True: #run forever
    sqrtof = (mpu.acceleration[0])**2 + (mpu.acceleration[1])**2 + (mpu.acceleration[2])**2 #total acceleration for all three axes
    totalaccel = math.sqrt(sqrtof) #this is the second part of the formula for the combined acceleration of all three axes
    print(totalaccel)
    if abs(totalaccel - normal)>threshold and steptrue == False: #When someone takes a step and the bool is false(meaning now it registers a step)
        steps = steps+1 # adds a step
        steptrue = 1 # sets the bool to true 
    elif abs(totalaccel-normal)>threshold and steptrue == True: #they still are over the threshold but have already met the condition before
        pass
    if abs(totalaccel-normal)<threshold and steptrue == True:   #the person was over the threshold but has now dipped under, setting the bool back to false
        steptrue = 0

        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        draw.text((42,0), f'{steps}', font=font, fill=255)
        print(f'Steps - {steps}') #this is when it will print the steps
    else: #too slow speed up
        pass
    display.image(image)
    display.show()
    time.sleep(0.01)






