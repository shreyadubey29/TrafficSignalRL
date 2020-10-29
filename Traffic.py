"""
Traffic generation code for sumo simulation
"""
import numpy as np
import warnings
warnings.filterwarnings("ignore")

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated):
        self.n_cars_generated = n_cars_generated
        self.max_steps = max_steps

    def create_route(self, seed):
        """
        creating route for each car for each episode
        """
        np.random.seed(seed)

        # car generation is as per normal distribution
        timings = np.random.normal(5000, 1200, self.n_cars_generated)
        timings = np.sort(timings)

        car_gen_steps = []

        for value in timings:
            car_gen_steps = np.append(
                car_gen_steps,
                (self.max_steps * abs(value)) / (np.max(timings) - np.min(timings)),
            )

        car_gen_steps = np.rint(car_gen_steps)

        # writing the route xml file
        with open("environment/episode_routes.rou.xml", "w") as routes:
            print(
                """<routes>
            <vType accel="1.0" decel="4.5" id="standard_car" length="5.0" minGap="2.5" maxSpeed="25" sigma="0.5" />
            <route id="W_N" edges="W2TL TL2N"/>
            <route id="W_E" edges="W2TL TL2E"/>
            <route id="W_S" edges="W2TL TL2S"/>
            <route id="N_W" edges="N2TL TL2W"/>
            <route id="N_E" edges="N2TL TL2E"/>
            <route id="N_S" edges="N2TL TL2S"/>
            <route id="E_W" edges="E2TL TL2W"/>
            <route id="E_N" edges="E2TL TL2N"/>
            <route id="E_S" edges="E2TL TL2S"/>
            <route id="S_W" edges="S2TL TL2W"/>
            <route id="S_N" edges="S2TL TL2N"/>
            <route id="S_E" edges="S2TL TL2E"/>""",
                file=routes,
            )

            for car_num, step in enumerate(car_gen_steps):
                str_or_turn_choice = np.random.uniform()
                if str_or_turn_choice < 0.75:
                    route_num = np.random.randint(1, 5)
                    if route_num == 1:
                        print(
                            '<vehicle id="W_E_%i" type="standard_car" route="W_E" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 2:
                        print(
                            '<vehicle id="N_S_%i" type="standard_car" route="N_S" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 3:
                        print(
                            '<vehicle id="E_W_%i" type="standard_car" route="E_W" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    else:
                        print(
                            '<vehicle id="S_N_%i" type="standard_car" route="S_N" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                else:
                    route_num = np.random.randint(1, 9)
                    if route_num == 1:
                        print(
                            '<vehicle id="W_N_%i" type="standard_car" route="W_N" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 2:
                        print(
                            '<vehicle id="W_S_%i" type="standard_car" route="W_S" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 3:
                        print(
                            '<vehicle id="E_N_%i" type="standard_car" route="E_N" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 4:
                        print(
                            '<vehicle id="E_S_%i" type="standard_car" route="E_S" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 5:
                        print(
                            '<vehicle id="N_W_%i" type="standard_car" route="N_W" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 6:
                        print(
                            '<vehicle id="N_E_%i" type="standard_car" route="N_E" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    elif route_num == 7:
                        print(
                            '<vehicle id="S_W_%i" type="standard_car" route="S_W" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )
                    else:
                        print(
                            '<vehicle id="S_E_%i" type="standard_car" route="S_E" depart="%s" departLane="random" departSpeed="10" />'
                            % (car_num, step),
                            file=routes,
                        )

            print("</routes>", file=routes)
