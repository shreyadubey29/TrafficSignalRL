"""
Code for Tools used in this project
"""

from sumolib import checkBinary
import os
import sys
import configparser
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

# function to set the sumo tool
def set_sumo(gui, sumocfg_file, max_steps):
    """
    Set SUMO parameters
    """
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ["SUMO_HOME"], "tools")
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")

    if gui == 0:
        sumoBinary = checkBinary("sumo")
    else:
        sumoBinary = checkBinary("sumo-gui")

    sumo_cmd = [
        sumoBinary,
        "-c",
        os.path.join("environment", sumocfg_file),
        "--no-step-log",
        "true",
        "--waiting-time-memory",
        str(max_steps),
    ]

    return sumo_cmd

# function to read config file
def set_config(config_file):
    config = configparser.ConfigParser()
    config.read_file(open(config_file))
    parameters = {}

    # path1 = config.get('My Section', 'path1')
    parameters["gui"] = int(config.get("simulation", "gui"))
    parameters["total_episodes"] = int(config.get("simulation", "total_episodes"))
    parameters["max_steps"] = int(config.get("simulation", "max_steps"))
    parameters["n_cars_generated"] = int(config.get("simulation", "n_cars_generated"))
    parameters["green_duration"] = int(config.get("simulation", "green_duration"))
    parameters["yellow_duration"] = int(config.get("simulation", "yellow_duration"))
    parameters["epochs"] = int(config.get("simulation", "epochs"))
    parameters["seed"] = int(config.get("simulation", "seed"))
    parameters["memory_size_min"] = int(config.get("memory", "memory_size_min"))
    parameters["memory_size_max"] = int(config.get("memory", "memory_size_max"))
    parameters["num_states"] = int(config.get("agent", "num_states"))
    parameters["num_actions"] = int(config.get("agent", "num_actions"))
    parameters["gamma"] = float(config.get("agent", "gamma"))
    parameters["batch_size"] = int(config.get("agent", "batch_size"))
    parameters["learning_rate"] = float(config.get("agent", "learning_rate"))
    parameters["models_path_name"] = config.get("dir", "models_path_name")
    parameters["sumocfg_file_name"] = config.get("dir", "sumocfg_file_name")
    parameters["test_model_path"] = config.get("dir", "test_model_path")
    parameters["base_model_path"] = config.get("dir", "base_model_path")

    return parameters

# function to save observation plots
def save_plot(path, data, filename, xlabel, ylabel):

    plt.plot(data)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    figure = plt.gcf()
    figure.savefig(os.path.join(path, filename + ".png"))
    plt.close("all")
