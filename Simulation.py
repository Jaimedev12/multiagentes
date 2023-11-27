from agent_models.Room import Room

class Simulation:
    def __init__(self, _M: int = 20, _N: int = 20,
                  _num_robots: int = 1, 
                  _modo_pos_inicial: str = '', 
                  _num_steps: int = 10,
                  _in_boxes_per_minute: int = 1,
                  _out_boxes_per_minute: int = 1,
                  _robot_positions: list = list()):
        
        self.simulation_actions = list()
        self.out_boxes_needed_in_steps = list()

        self.num_steps = _num_steps
        
        mapped_robot_positions = [(pos['x'], pos['z']) for pos in _robot_positions]
        self.starter_model = Room(M=_M, N=_N, 
                                  num_robots=_num_robots, 
                                  modo_pos_inicial=_modo_pos_inicial,
                                  in_boxes_per_minute=_in_boxes_per_minute,
                                  out_boxes_per_minute=_out_boxes_per_minute,
                                  robot_positions=mapped_robot_positions)

    def execute_simulation(self):
        self.simulation_actions = list()
        self.out_boxes_needed_in_steps = list()

        for i in range(self.num_steps):
            self.starter_model.step()
            self.out_boxes_needed_in_steps.append(self.starter_model.shipment_orders_pending)

        self.simulation_actions = self.starter_model.datacollector.model_vars['AgentActions']
            