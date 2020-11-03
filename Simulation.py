# -*- coding: utf-8 -*-
"""
Code for running simulation for the traffic signal by the RL agent
"""
import numpy as np
import traci
import timeit
import random

import warnings

warnings.filterwarnings("ignore")

"""
    we only have 4 actions that the agent can take which are of turning the 
    lights green because the yellow lights will be the consequence of the 
    decision and they will be the intemediate action that will happen if the
    traffic light changes from red to green or vice versa
"""
# actions
# action 0 - 00
NS_GREEN = 0
NS_YELLOW = 1
# action 1 - 01
NSL_GREEN = 2
NSL_YELLOW = 3
# action 2 - 10
EW_GREEN = 4
EW_YELLOW = 5
# action 3 - 11
EWL_GREEN = 6
EWL_YELLOW = 7


class Simulation:

    # class variables
    def __init__(
        self,
        Model,
        Memory,
        Traffic_gen,
        sumo_cmd,
        gamma,
        max_steps,
        green_duration,
        yellow_duration,
        num_states,
        num_actions,
        epochs,
    ):
        self.Model = Model
        self.Memory = Memory
        self.Traffic_gen = Traffic_gen
        self.gamma = gamma
        self.step_count = 0
        self.sumo_cmd = sumo_cmd
        self.max_steps = max_steps
        self.yellow_duration = yellow_duration
        self.green_duration = green_duration
        self.num_of_states = num_states
        self.num_of_actions = num_actions
        self.rewards_list = []
        self.cumulative_wait_time_list = []
        self.average_queue_length_list = []
        self.epochs = epochs

    def run(self, episode, epsilon):
        """
        This function will run one episode and then it will start the training for the agent
        """
        start_time = timeit.default_timer()

        # setup sumo
        self.Traffic_gen.create_route(episode)
        traci.start(self.sumo_cmd)

        # initialize variables in start of episode
        self.step_count = 0
        self.waiting_times = {}
        self.sum_queue_length = 0
        self.sum_waiting_time = 0
        self.episode_reward = 0
        old_total_wait_time = 0
        old_state = -1
        old_action = -1

        while self.step_count < self.max_steps:

            # get current state
            current_state = self.get_state()

            # get reward for previous action
            current_total_wait = self.collect_waiting_times()
            reward = self.get_reward(old_total_wait_time, current_total_wait)

            # saving data into memory
            if self.step_count > 0:
                self.Memory.add_sample((old_state, old_action, reward, current_state))

            # choose action based on the current state
            action = self.choose_action(current_state, epsilon)

            # check if the action chosen is different from the last action then activate yellow lights
            if self.step_count != 0 and action != old_action:
                self.activate_yellow_lights(old_action)
                self.simulate(self.yellow_duration)

            # take the chosen action
            self.activate_green_lights(action)
            self.simulate(self.green_duration)

            # updating the variables for next step
            old_state = current_state
            old_action = action
            old_total_wait_time = current_total_wait

            self.episode_reward = self.episode_reward + reward

        # save episode stats
        self.save_episode_stats()
        print("Total reward:", self.episode_reward, "| Epsilon: ", round(epsilon, 2))
        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        # now start training
        train_start_time = timeit.default_timer()
        for e in range(self.epochs):
            self.replay()

        training_time = round(timeit.default_timer() - train_start_time, 1)

        return simulation_time, training_time

    def get_state(self):
        state = np.zeros(self.num_of_states)

        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            lane_position = traci.vehicle.getLanePosition(car_id)
            lane_id = traci.vehicle.getLaneID(car_id)
            # manipulating the value so that the nearest car near the traffic light has position 0
            lane_position = 750 - lane_position

            if lane_position < 8:
                cell_no = 0
            elif lane_position < 16:
                cell_no = 1
            elif lane_position < 32:
                cell_no = 2
            elif lane_position < 64:
                cell_no = 3
            elif lane_position < 128:
                cell_no = 4
            elif lane_position < 256:
                cell_no = 5
            elif lane_position < 330:
                cell_no = 6
            elif lane_position < 500:
                cell_no = 7
            elif lane_position < 630:
                cell_no = 8
            elif lane_position < 750:
                cell_no = 9

            # finding cell prefix from lane id
            if lane_id == "W2TL_0":
                cell_prefix = 0
            elif lane_id == "W2TL_1":
                cell_prefix = 1
            elif lane_id == "N2TL_0":
                cell_prefix = 2
            elif lane_id == "N2TL_1":
                cell_prefix = 3
            elif lane_id == "E2TL_0":
                cell_prefix = 4
            elif lane_id == "E2TL_1":
                cell_prefix = 5
            elif lane_id == "S2TL_0":
                cell_prefix = 6
            elif lane_id == "S2TL_1":
                cell_prefix = 7
            else:
                cell_prefix = -1

            if cell_prefix >= 1 and cell_prefix <= 7:
                car_cell = int(str(cell_prefix) + str(cell_no))
                valid_car = True
            elif cell_prefix == 0:
                car_cell = cell_no
                valid_car = True
            else:
                # cars that are crossing or have crossed the intersection are not valid
                valid_car = False

            if valid_car:
                state[car_cell] = 1

        return state

    def get_reward(self, old_wait_time, current_wait_time):
        reward = 0
        reward = old_wait_time - current_wait_time
        return reward

    def choose_action(self, state, epsilon):
        """
        This function decides if we will explore or exploit in this step
        """
        if random.random() < epsilon:
            return random.randint(0, self.num_of_actions - 1)
        else:
            return np.argmax(self.Model.predict_single(state))

    def activate_yellow_lights(self, action):
        yellow_code = action * 2 + 1
        traci.trafficlight.setPhase("TL", yellow_code)

    def activate_green_lights(self, action):
        if action == 0:
            traci.trafficlight.setPhase("TL", NS_GREEN)
        elif action == 1:
            traci.trafficlight.setPhase("TL", NSL_GREEN)
        elif action == 2:
            traci.trafficlight.setPhase("TL", EW_GREEN)
        elif action == 3:
            traci.trafficlight.setPhase("TL", EWL_GREEN)

    def get_queue_length(self):
        """
        Calculate the total number of cars at speed = 0 in each incoming lane
        """
        N_lane = traci.edge.getLastStepHaltingNumber("N2TL")
        S_lane = traci.edge.getLastStepHaltingNumber("S2TL")
        E_lane = traci.edge.getLastStepHaltingNumber("E2TL")
        W_lane = traci.edge.getLastStepHaltingNumber("W2TL")

        total_queue_length = N_lane + S_lane + W_lane + E_lane
        return total_queue_length

    def save_episode_stats(self):
        self.rewards_list.append(self.episode_reward)
        self.cumulative_wait_time_list.append(self.sum_waiting_time)
        self.average_queue_length_list.append(self.sum_queue_length)

    def simulate(self, steps_todo):
        """
        Perform steps in sumo
        """
        if (self.step_count + steps_todo) >= self.max_steps:
            steps_todo = self.max_steps - self.step_count

        while steps_todo > 0:
            traci.simulationStep()
            self.step_count += 1
            steps_todo -= 1
            queue_length = self.get_queue_length()
            self.sum_queue_length += queue_length
            self.sum_waiting_time += queue_length

    def collect_waiting_times(self):
        """
        Get waiting time for every car on the incoming roads
        """
        incoming_roads = ["E2TL", "N2TL", "W2TL", "S2TL"]
        car_list = traci.vehicle.getIDList()

        for car_id in car_list:
            wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
            road_id = traci.vehicle.getRoadID(car_id)
            if road_id in incoming_roads:
                self.waiting_times[car_id] = wait_time
            else:
                if car_id in self.waiting_times:
                    del self.waiting_times[car_id]

        total_waiting_time = sum(self.waiting_times.values())
        return total_waiting_time

    def replay(self):
        """`
        Get samples from memory and then use them to update the learning equation and then train
        """
        batch = self.Memory.get_samples(self.Model.batch_size)

        if len(batch) > 0:
            states = np.array([val[0] for val in batch])
            next_states = np.array([val[3] for val in batch])

            # prediction
            current_qsa_value = self.Model.predict_batch(states)
            next_qsa_value = self.Model.predict_batch(next_states)

            # set x and y arrays for training
            x = np.zeros((len(batch), self.num_of_states))
            y = np.zeros((len(batch), self.num_of_actions))

            n = 0
            for b in batch:
                state, action, reward, next_state = b[0], b[1], b[2], b[3]
                current_q = current_qsa_value[n]
                current_q[action] = reward + self.gamma * np.amax(next_qsa_value[n])
                x[n] = state
                y[n] = current_q
                n += 1

            self.Model.train_model(x, y)
