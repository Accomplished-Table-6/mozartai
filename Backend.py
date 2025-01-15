import tensorflow as tf
import keras
import os
import numpy as np




model = tf.keras.models.Sequential([
tf.keras.layers.Conv2D(filters=16,kernel_size=(3,3),activation="relu",input_shap="64,64,3"),
tf.keras.layers.MaxPool2D(),
tf.keras.layers.Conv2D(filters=32,kernel_size=(3,3),activation="relu"),
tf.keras.layers.MaxPool2D(),
tf.keras.layers.Conv2D(filters=64,kernel_size=(3,3),activation="relu"),
tf.keras.layers.MaxPool2D(), 
tf.keras.layers.Conv2D(filters=128,kernel_size=(3,3),activation="relu"),
tf.keras.layers.Flatten(),
tf.keras.layers.Dense(units=128,activation="relu"),
tf.keras.layers.Dense(units=64,activation="relu"),
tf.keras.layers.Dense(units=36,activation="softmax")
])