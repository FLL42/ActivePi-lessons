# Not for Raspberry Pi because of limited computing power.
# Based on https://colab.research.google.com/github/arduino/ArduinoTensorFlowLiteTutorials/blob/master/GestureToEmoji/arduino_tinyml_workshop.ipynb
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

print(f"TensorFlow version = {tf.__version__}\n")

# Set a fixed random seed value, for reproducibility, this will allow us to get
# the same random numbers each time the notebook is run
SEED = int(int.from_bytes('ActivePi'.encode(), 'little') / 100000000000)
np.random.seed(SEED)
tf.random.set_seed(SEED)

# the list of gestures that data is available for
GESTURES = [
    "step",
    "no_step",
]

SAMPLES_PER_GESTURE = 100

NUM_GESTURES = len(GESTURES)

# create a one-hot encoded matrix that is used in the output
ONE_HOT_ENCODED_GESTURES = np.eye(NUM_GESTURES)

inputs = []
outputs = []

# read each csv file and push an input and output
for gesture_index in range(NUM_GESTURES):
  gesture = GESTURES[gesture_index]
  print(f"Processing index {gesture_index} for gesture '{gesture}'.")
  
  output = ONE_HOT_ENCODED_GESTURES[gesture_index]
  
  df = pd.read_csv("./" + gesture + ".csv")
  
  # calculate the number of gesture recordings in the file
  num_recordings = int(df.shape[0] / SAMPLES_PER_GESTURE)
  
  print(f"\tThere are {num_recordings} recordings of the {gesture} gesture.")
  
  for i in range(num_recordings):
    tensor = []
    for j in range(SAMPLES_PER_GESTURE):
      index = i * SAMPLES_PER_GESTURE + j
      # normalize the input data, between 0 to 1:
      # - acceleration is between: -4 to +4
      # - gyroscope is between: -2000 to +2000
      tensor += [
          (df['acc_x'][index] + 9.80665) / (9.80665 * 2),
          (df['acc_y'][index] + 9.80665) / (9.80665 * 2),
          (df['acc_z'][index] + 9.80665) / (9.80665 * 2),
          (df['gyro_x'][index] + 250.138) / (250.138 * 2),
          (df['gyro_y'][index] + 250.138) / (250.138 * 2),
          (df['gyro_z'][index] + 250.138) / (250.138 * 2)
      ]

    inputs.append(tensor)
    outputs.append(output)

# convert the list to numpy array
inputs = np.array(inputs)
outputs = np.array(outputs)

print("Data set parsing and preparation complete.")

# Randomize the order of the inputs, so they can be evenly distributed for training, testing, and validation
# https://stackoverflow.com/a/37710486/2020087
num_inputs = len(inputs)
randomize = np.arange(num_inputs)
np.random.shuffle(randomize)

# Swap the consecutive indexes (0, 1, 2, etc) with the randomized indexes
inputs = inputs[randomize]
outputs = outputs[randomize]

# Split the recordings (group of samples) into three sets: training, testing and validation
TRAIN_SPLIT = int(0.6 * num_inputs)
TEST_SPLIT = int(0.2 * num_inputs + TRAIN_SPLIT)

inputs_train, inputs_test, inputs_validate = np.split(inputs, [TRAIN_SPLIT, TEST_SPLIT])
outputs_train, outputs_test, outputs_validate = np.split(outputs, [TRAIN_SPLIT, TEST_SPLIT])

print("Data set randomization and splitting complete.")

# build the model and train it
model = tf.keras.Sequential()
model.add(tf.keras.layers.LeakyReLU(alpha=0.18, input_shape=(600,)))
model.add(tf.keras.layers.Reshape((100, 6)))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.MaxPool1D(3))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.MaxPool1D(3))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.Conv1D(50, 3, activation='relu'))
model.add(tf.keras.layers.MaxPool1D(2))
model.add(tf.keras.layers.Flatten())
model.add(tf.keras.layers.LeakyReLU(alpha=0.18))
model.add(tf.keras.layers.Dense(50, activation='relu'))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(18, activation='relu'))
model.add(tf.keras.layers.Dropout(0.2))
model.add(tf.keras.layers.Dense(NUM_GESTURES, activation='softmax')) # softmax is used, because we only expect one gesture to occur per input
model.compile(optimizer='adam', loss='mse', metrics=['acc', 'mae'])
model.summary()
history = model.fit(inputs_train, outputs_train, epochs=50, batch_size=1, validation_data=(inputs_validate, outputs_validate))

model.summary()

# increase the size of the graphs. The default size is (6,4).
plt.rcParams["figure.figsize"] = (20,10)

# graph the loss, the model above is configure to use "mean squared error" as the loss function
acc = history.history['acc']
val_acc = history.history['val_acc']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'g', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

print(plt.rcParams["figure.figsize"])

model.save('model.h5')

# use the model to predict the test inputs
predictions = model.predict(inputs_test)

# print the predictions and the expected ouputs
print("predictions =\n", np.round(predictions, decimals=5))
print("actual =\n", outputs_test)

for i in range(len(predictions)):
    a = list(outputs_test)[i][0] # if it is a step
    p = list(predictions)[i][0] # predicted chance of it being a step
    print(f"Actual: {a}, Predicted: {p * 100}%")

# Plot the predictions along with to the test data
plt.clf()
plt.title('Training data predicted vs actual values, difference -- 0 is best')
plt.plot(range(len(predictions)), [abs(predictions[i] - outputs_test[i]) for i in range(len(predictions))], 'y.', label='difference')
mean = 0
for i in [abs(predictions[i] - outputs_test[i]) for i in range(len(predictions))]:
  mean += i
mean /= len(predictions)
plt.plot([0, len(predictions) - 1], [mean, mean], 'b', label='mean')
plt.show()

# Convert the model to the TensorFlow Lite format without quantization
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save the model to disk
open("model.tflite", "wb").write(tflite_model)