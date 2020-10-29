# -*- coding: utf-8 -*-
"""
Neural network model for getting action for current state
"""
import numpy as np
import keras    
from keras import layers, losses, optimizers, Input
from keras.utils import plot_model
import os
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

class TrainingModel:
    def __init__(self, input_dim, output_dim, batch_size, learning_rate):

        # hyperparameters
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.batch_size = batch_size
        self.learning_rate = learning_rate

        # now build and compile the model
        inputs = Input(shape=(self.input_dim,))

        layer1 = layers.Dense(200, activation="relu")(inputs)
        layer2 = layers.Dense(200, activation="relu")(layer1)
        layer3 = layers.Dense(200, activation="relu")(layer2)
        layer4 = layers.Dense(200, activation="relu")(layer3)

        outputs = layers.Dense(self.output_dim, activation="softmax")(layer4)

        self.model = keras.Model(inputs=inputs, output=outputs)

        # using mean sqaured error loss and Adam optimizer
        self.model.compile(
            loss=losses.mean_squared_error,
            optimizer=optimizers.Adam(lr=self.learning_rate),
        )

    def predict_single(self, state):

        # predict action value for a single state
        state = np.reshape(state, [1, self.input_dim])
        return self.model.predict(state)

    def predict_batch(self, states):

        # predict action values for a bacth of states
        return self.model.predict(states)

    def train_model(self, input_states, target_q_s_a):

        # train the model
        self.model.fit(input_states, target_q_s_a, epochs=10, verbose=0)

    def save_model(self, path):
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Save the current model
        self.model.save(
            os.path.join(
                path, "trained_model_" + timestamp + ".h5"
            )
        )
#        plot_model(
#            self.model,
#            to_file=os.path.join(path, "model_" + timestamp + ".png"),
#            show_shapes=True,
#            show_layer_names=True,
#        )
