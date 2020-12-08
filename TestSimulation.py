"""
Code for running simulation for the traffic signal by the RL agent
"""
import numpy as np
import traci
import timeit

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


class TestSimulation:

    # class variables
    def __init__(
        self,
        Model,
        Traffic_gen,
        sumo_cmd,
        max_steps,
        green_duration,
        yellow_duration,
        num_states,
        num_actions,
    ):
        self.Model = Model
        self.Traffic_gen = Traffic_gen
        self.step_count = 0
        self.sumo_cmd = sumo_cmd
        self.max_steps = max_steps
        self.yellow_duration = yellow_duration
        self.green_duration = green_duration
        self.num_of_states = num_states
        self.num_of_actions = num_actions
        self.rewards_list = []
        self.queue_length_list = []
        self.wait_time_list = []

    def run_test(self, episode):
        """
        Runs the test simulation
        """
        start_time = timeit.default_timer()

        self.Traffic_gen.create_route(episode)
        traci.start(self.sumo_cmd)

        self.step_count = 0
        self.waiting_times = {}
        old_total_wait_time = 0
        old_action = -1

        while self.step_count < self.max_steps:

            current_state = self.get_state()
            current_total_wait = self.collect_waiting_times()

            reward = self.get_reward(old_total_wait_time, current_total_wait)
            action = self.choose_test_action(current_state)
            
            if self.step_count != 0 and old_action != action:
                self.activate_yellow_lights(old_action)
                self.simulate(self.yellow_duration)

            self.activate_green_lights(action)
            self.simulate(self.green_duration)

            self.wait_time_list.append(current_total_wait)
            
            old_action = action
            old_total_wait_time = current_total_wait

            self.rewards_list.append(reward)

        traci.close()
        simulation_time = round(timeit.default_timer() - start_time, 1)

        return simulation_time
    
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
                if state[car_cell] == 0:
                    state[car_cell] = 1
                else:
                    state[car_cell] +=1

        return state

    # function to get reward
    def get_reward(self, old_wait_time, current_wait_time):
        reward = 0
        reward = old_wait_time - current_wait_time
        return reward

    # function to start yellow light
    def activate_yellow_lights(self, action):
        yellow_code = action * 2 + 1
        traci.trafficlight.setPhase("TL", yellow_code)
        
    # function to start green light 
    def activate_green_lights(self, action):
        if action == 0:
            traci.trafficlight.setPhase("TL", NS_GREEN)
        elif action == 1:
            traci.trafficlight.setPhase("TL", NSL_GREEN)
        elif action == 2:
            traci.trafficlight.setPhase("TL", EW_GREEN)
        elif action == 3:
            traci.trafficlight.setPhase("TL", EWL_GREEN)
            
    # function to get number of cars waiting
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
    
    # function to simulate the enviornment on sumo
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
            self.queue_length_list.append(queue_length)

    # function to collect cumulative wait time
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
    
    # function to take action using the trained model
    def choose_test_action(self, state):
        return np.argmax(self.Model.predict_single(state))
