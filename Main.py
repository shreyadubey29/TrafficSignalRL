"""
Main function for starting the Reinforcement Learning
"""
from Model import TrainingModel
from Memory import Memory
from Traffic import TrafficGenerator
from Simulation import Simulation
from datetime import datetime
from Tools import set_config, set_sumo

import warnings
warnings.filterwarnings("ignore")

def main():
    
    config = set_config("config_parameters.txt")
    sumo_cmd = set_sumo(config["gui"], config["sumocfg_file_name"], config["max_steps"])
    Model = TrainingModel(
        config["num_states"],
        config["num_actions"],
        config["batch_size"],
        config["learning_rate"],
    )
    memory = Memory(config["memory_size_min"], config["memory_size_max"])
    Traffic_gen = TrafficGenerator(config["max_steps"], config["n_cars_generated"])
    simulation = Simulation(
        Model,
        memory,
        Traffic_gen,
        sumo_cmd,
        config["gamma"],
        config["max_steps"],
        config["green_duration"],
        config["yellow_duration"],
        config["num_states"],
        config["num_actions"],
        config["epochs"],
    )
    episode = 0

    start_time = datetime.now()
    print("Start time: ", start_time.strftime("%Y%m%d_%H%M%S"))

    # 90% exploration, 10% exploitation
    epsilon = 0.9
    # exploration decays by this factor every episode
    epsilon_decay = 0.9
    # in the long run, 10% exploration, 90% exploitation
    epsilon_min = 0.1
    
    while episode < config["total_episodes"]:

        print("Episode: ", episode + 1)
        simulation_time, training_time = simulation.run(episode, epsilon)
        print("Simulation time: ", simulation_time, "sec")
        print("Training time: ", training_time, "sec")
        print("Total time: ", round(simulation_time + training_time, 1), "sec")

        episode += 1
        epsilon = update_epsilon(epsilon, epsilon_min, epsilon_decay)

    path = r"C:\Users\khare\Desktop\Study\Fall2020\Courses\AI with Reinforcement Learning\Project\Code\Models"
    Model.save_model(path)
    print("End time: ", datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("Model saved at the path: ", path)


def update_epsilon(epsilon, epsilon_min, epsilon_decay):
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay
    return epsilon


main()
