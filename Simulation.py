from agent_models.Room import Room

class Simulation:
    def __init__(self, _M: int = 20, _N: int = 20,
                  _num_robots: int = 1, 
                  _modo_pos_inicial: str = '', 
                  _num_steps: int = 10,
                  robot_positions: list = list()):
        self.simulation_actions = list()
        self.num_steps = _num_steps
        
        mapped_robot_positions = [(pos['x'], pos['z']) for pos in robot_positions]
        self.starter_model = Room(M=_M, N=_N, 
                                  num_robots=_num_robots, 
                                  modo_pos_inicial=_modo_pos_inicial,
                                  robot_positions=mapped_robot_positions)

    def execute_simulation(self):
        self.simulation_actions = list()

        for i in range(self.num_steps):
            print("Ejecutando paso ", i)
            self.starter_model.step()

        print("Se ejecutaron todos los pasos de la simulación")

        self.simulation_actions = self.starter_model.datacollector.model_vars['AgentActions']
            
        for i in range(len(self.simulation_actions)):
            print("Action: ", self.simulation_actions[i], "\n")