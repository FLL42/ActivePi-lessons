from adafruit_extended_bus import ExtendedI2C as I2C # sudo pip3 install adafruit-extended-bus
import adafruit_mpu6050 # sudo pip3 install adafruit-circuitpython-mpu6050
import board, digitalio, math, time
import numpy as np
from tensorflow import lite as tflite

i2c = I2C(11)

accelerometer = adafruit_mpu6050.MPU6050(i2c)

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
            sample_list += [
                (sample[0] + 9.80665) / (9.80665 * 2),
                (sample[1] + 9.80665) / (9.80665 * 2),
                (sample[2] + 9.80665) / (9.80665 * 2),
                (sample[3] + 250.138) / (250.138 * 2),
                (sample[4] + 250.138) / (250.138 * 2),
                (sample[5] + 250.138) / (250.138 * 2)
            ]
            last_time = time.time_ns() / 1000000000
            sample_count += 1
        time.sleep(0.001)
    return sample_list

def infer(sample_list):
    # Load the TFLite model and allocate tensors.
    interpreter = tflite.Interpreter(model_path="model.tflite")
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(input_details)

    sample_list = np.array(np.asarray(sample_list, dtype=np.float32))
    print(sample_list.dtype)
    print(sample_list.shape)

    interpreter.set_tensor(input_details[0]['index'], [sample_list])

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index'])
    return output_data

sample_list = []

def check():
    sample = accelerometer.acceleration
    if total_acceleration(subtract_lists(sample, calibration)) > threshold:
        print(infer(get_sample()))

print("hi!")

while True:
    check()
    time.sleep(0.01)