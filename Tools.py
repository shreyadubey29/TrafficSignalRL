"""
Code for Tools used in this project
"""

from sumolib import checkBinary
import os
import sys
import ConfigParser
import matplotlib.pyplot as plt

def set_sumo(gui, sumocfg_file, max_steps):
    """
    Set SUMO parameters
    """
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")
        
    if gui == False:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')
        
    sumo_cmd = [sumoBinary, "-c", os.path.join('intersection', sumocfg_file),
                "--no-step-log", "true", "--waiting-time-memory", str(max_steps)]
    
    return sumo_cmd
    
def set_config(config_file):
    config = ConfigParser.ConfigParser()
    config.read_file(open(r'config.txt'))
    parameters = {}
    
    #path1 = config.get('My Section', 'path1')
    parameters['gui'] = config.get('simulation', 'gui')
    parameters['total_episodes'] = config.get('simulation', 'total_episodes')
    parameters['max_steps'] = config.get('simulation', 'max_steps')
    parameters['n_cars_generated'] = config.get('simulation', 'n_cars_generated')
    parameters['green_duration'] = config.get('simulation', 'green_duration')
    parameters['yellow_duration'] = config.get('simulation', 'yellow_duration')
    parameters['memory_size_min'] = config.get('memory', 'memory_size_min')
    parameters['memory_size_max'] = config.get('memory', 'memory_size_max')
    parameters['num_states'] = config.get('agent', 'num_states')
    parameters['num_actions'] = config.get('agent', 'num_actions')
    parameters['gamma'] = config.get('agent', 'gamma')
    parameters['models_path_name'] = config.get('dir', 'models_path_name')
    parameters['sumocfg_file_name'] = config.get('dir', 'sumocfg_file_name')
    
    return parameters
    
    
def save_plot(path, data, filename, xlabel, ylabel):
    
    plt.plot(data)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    
    figure = plt.gcf()
    figure.savefig(os.path.join(path, filename + '.png'))
    plt.close("all")
    
    