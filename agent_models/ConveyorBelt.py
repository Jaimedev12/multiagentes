from mesa.agent import Agent    

class ConveyorBelt(Agent):
    def __init__(self, unique_id, model, direction: tuple, is_spawn_point: bool = False):
        super().__init__(unique_id, model)
        self.direction = direction
        self.is_spawn_point = is_spawn_point