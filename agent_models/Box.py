from mesa.agent import Agent

class Box(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_apartada = False