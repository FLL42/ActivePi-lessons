from adafruit_extended_bus import ExtendedI2C as I2C # sudo pip3 install adafruit-extended-bus
import adafruit_mpu6050 # sudo pip3 install adafruit-circuitpython-mpu6050
import board, digitalio, math, time

i2c = I2C(11)

accelerometer = adafruit_mpu6050.MPU6050(i2c)

print("This is the step counter training program, for aspiring AI-powered step counters.")

print("Calibration time!")
calibration = []

def calibrate():
    global calibration
    total = [0, 0, 0]
    for i in range(100):
        acceleration = accelerometer.acceleration
        total[0] += acceleration[0]
        total[1] += acceleration[1]
        total[2] += acceleration[2]
    total[0] /= 100.0
    total[1] /= 100.0
    total[2] /= 100.0
    calibration = total

calibrate()

print("Can you help by stepping?")

threshold = 5 # m / s^2

samples = 100

def subtract_lists(a, b):
    final_list = []
    if len(a) != len(b):
        return None
    for i in range(len(a)):
        final_list.append(a[i] - b[i])
    return final_list

def total_acceleration(sample):
    return math.sqrt(sample[0]**2 + sample[1]**2 + sample[2]**2) # thanks Kunal

def get_sample():
    sample_list = []
    sample_count = 0
    last_time = time.time_ns() / 1000000000
    while sample_count < 100:
        if time.time() - last_time >= 0.01:
            sample = list(accelerometer.acceleration)
            sample.extend(list(accelerometer.gyro))
            sample_list.append(sample)
            last_time = time.time_ns() / 1000000000
            sample_count += 1
        time.sleep(0.001)
    print("done")
    return sample_list

sample_list = []

def check():
    # sample = accelerometer.acceleration
    # if total_acceleration(subtract_lists(sample, calibration)) > threshold:
    #     print("pickles")
    if not button.value:
        print("pickles")
        sample_list.append(get_sample())

def write_samples():
    with open("step.csv", "w") as f:
        to_write = "acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z\n"
        for sample in sample_list:
            line = ""
            for i in sample:
                line += f"{i},"
                line = line[:-1] # remove last ,
                line += "\n"
            to_write += line+"\n"
        f.write(to_write)

button = digitalio.DigitalInOut(board.D26)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

while True:
    try:
        check()
        time.sleep(0.01)
    except KeyboardInterrupt:
        write_samples()
        raise KeyboardInterrupt