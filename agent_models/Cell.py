from mesa.agent import Agent    

class Cell(Agent):
    def __init__(self, unique_id, model, is_apartada: bool = False):
        super().__init__(unique_id, model)
        self.is_apartada = is_apartada