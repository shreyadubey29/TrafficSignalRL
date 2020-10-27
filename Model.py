# -*- coding: utf-8 -*-
"""
Neural network model for getting action for current state
"""
import numpy as np
import keras
from keras import layers, losses, optimizers
from keras.utils import plot_model
import os

class TrainingModel:
    def __init__(self):
        
        # hyperparameters
        self.input_dim = 80
        self.output_dim = 4
        self.batch_size = 50
        self.learning_rate = 0.01
        
        # now build and compile the model
        inputs = keras.Input(shape=(self.input_dim,))
        
        layer1 = layers.Dense(200, activation='relu')(inputs)
        layer2 = layers.Dense(200,activation='relu')(layer1)
        layer3 = layers.Dense(200,activation='relu')(layer2)
        layer4 = layers.Dense(200,activation='relu')(layer3)
        
        outputs = layers.Dense(self.output_dim, activation='softmax')(layer4)
        
        model = keras.Model(inputs=inputs, output=outputs)
        
        # using mean sqaured error loss and Adam optimizer
        model.compile(loss=losses.mean_squared_error, optimizer=optimizers.Adam(lr=self.learning_rate))
        
        return model
    
    def predict_single(self, state):
        
        # predict action value for a single state
        state = np.reshape(state,[1, self.input_dim])
        return self.model.predict(state)
    
    def predict_batch(self, states):
        
        # predict action values for a bacth of states
        return self.model.predict(states)
        
    def train_model(self, input_states, target_q_s_a):
        
        # train the model
        self.model.fit(input_states, target_q_s_a, epochs=1, verbose=0)
        
    def save_model(self, path):
        
        # Save the current model
        self.model.save(os.path.join(path,'trained_model.h5'))
        plot_model(self.model, to_file=os.path.join(path, 'model.png'), show_shapes=True, show_layer_name=True)
        