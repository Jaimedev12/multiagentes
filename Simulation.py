from agent_models.Room import Room

class Simulation:
    def __init__(self, _M: int = 20, _N: int = 20, _num_robots: int = 1, _modo_pos_inicial: str = 'Aleatoria', _num_steps: int = 10):
        self.simulation_actions = list()
        self.starter_model = Room(M=_M, N=_N, num_robots=_num_robots, modo_pos_inicial=_modo_pos_inicial)
        self.num_steps = _num_steps

    def execute_simulation(self):
        self.simulation_actions = list()

        for i in range(self.num_steps):
            self.starter_model.step()

        self.simulation_actions = self.starter_model.datacollector.model_vars['AgentActions']
            
        for i in range(len(self.simulation_actions)):
            print("Action: ", self.simulation_actions[i], "\n")