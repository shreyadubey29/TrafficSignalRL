"""
Main function for starting the Reinforcement Learning
"""
from Model import TrainingModel, TestModel
from Memory import Memory
from Traffic import TrafficGenerator
from Simulation import Simulation
from TestSimulation import TestSimulation
from datetime import datetime
from Tools import set_config, set_sumo, save_plot
import argparse

import warnings

warnings.filterwarnings("ignore")


def main():
    parser = argparse.ArgumentParser(description="model mode")

    parser.add_argument("--mode", "-m", dest="mode", default="2")

    args = parser.parse_args()

    if args.mode == "1":
        print("training")
        train_model()
    elif args.mode == "2":
        print("testing")
        test_model()
    elif args.mode == "3":
        print("training and testing")
        train_model()
        test_model()


def train_model():
    config = set_config("config_parameters.txt")
    sumo_cmd = set_sumo(config["gui"], config["sumocfg_file_name"], config["max_steps"])
    path = config["models_path_name"]

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
        print("---------------------------------------------------------------------")
        print("Episode: ", episode + 1)
        simulation_time, training_time = simulation.run(episode, epsilon)
        print("Simulation time: ", simulation_time, "sec")
        print("Training time: ", training_time, "sec")
        print("Total time: ", round(simulation_time + training_time, 1), "sec")

        episode += 1
        epsilon = update_epsilon(epsilon, epsilon_min, epsilon_decay)

    # path = r"C:\Users\khare\Desktop\Study\Fall2020\Courses\AI with Reinforcement Learning\Project\Code\Models"
    Model.save_model(path)
    print("End time: ", datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("Model saved at the path: ", path)
    save_plot(path, simulation.rewards_list, "reward", "Episode", "Cumulative Reward")
    save_plot(
        path,
        simulation.cumulative_wait_time_list,
        "delay",
        "Episode",
        "Cumulative Delay",
    )
    save_plot(
        path,
        simulation.average_queue_length_list,
        "queue",
        "Episode",
        "Avg queue length",
    )


def update_epsilon(epsilon, epsilon_min, epsilon_decay):
    if epsilon > epsilon_min:
        epsilon *= epsilon_decay
    return epsilon


def test_model():

    config = set_config("config_parameters.txt")
    sumo_cmd = set_sumo(config["gui"], config["sumocfg_file_name"], config["max_steps"])
    test_path = config["test_model_path"]
    model_path = config["models_path_name"]

    model = TestModel(config["num_states"], model_path)
    traffic_gen = TrafficGenerator(config["max_steps"], config["n_cars_generated"])
    
    print("Make Simulation object")
    
    simulation = TestSimulation(
        model,
        traffic_gen,
        sumo_cmd,
        config["max_steps"],
        config["green_duration"],
        config["yellow_duration"],
        config["num_states"],
        config["num_actions"],
    )

    print("Test episode")

    simulation_time = simulation.run_test(config["seed"])
    print("Simulation time: ", simulation_time, "sec")
    save_plot(
        test_path,
        simulation.rewards_list,
        "reward",
        "steps",
        "Rewards",
    )
    save_plot(
        test_path,
        simulation.queue_length_list,
        "queue length",
        "steps",
        "Queue Length",
    )
    print("Testing results saved at ", test_path)

main()
