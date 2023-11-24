from mesa.agent import Agent    

class ConveyorBelt(Agent):
    def __init__(self, unique_id, model, direction: tuple):
        super().__init__(unique_id, model)
        self.direction = direction