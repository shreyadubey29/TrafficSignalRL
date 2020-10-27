"""
Main function for starting the Reinforcement Learning
"""
from Model import Model
#import Memory
#import Traffic
from Simulation import Simulation
from datetime import datetime

def main():
    #sumo_cmd = set_sumo()
    model = Model.TrainingModel()
    simulation = Simulation(model)
    total_episodes = 100
    episode = 0
    
    start_time = datetime.now()
    print("Start time: ", start_time.strftime("%Y%m%d_%H%M%S"))
    
    while episode < total_episodes:
        
        print("Episode: ", episode+1)
        # 90% exploration, 10% exploitation
        epsilon = 0.9
        # exploration decays by this factor every episode
        epsilon_decay = 0.9
        # in the long run, 10% exploration, 90% exploitation
        epsilon_min = 0.1
        
        simulation_time, training_time = simulation.run(episode, epsilon)
        print("Simulation time: ", simulation_time, "sec")
        print("Traing time: ", training_time, "sec")
        print("Toatal time: ", round(simulation_time + training_time, 1), "sec")
        
        episode +=1
        update_epsilon(epsilon, epsilon_min, epsilon_decay)
        
    path = r"C:\Users\khare\Desktop\Study\Fall2020\Courses\AI with Reinforcement Learning\Project\Code\Models"
    Model.save_model()
    print("End time: ", datetime.now().strftime("%Y%m%d_%H%M%S"))
    print("Model saved at the path: ", path)
    
def update_epsilon(epsilon, epsilon_min, epsilon_decay):
    if epsilon > epsilon_min:
            epsilon *= epsilon_decay