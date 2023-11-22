from mesa.agent import Agent    

class Shelf(Agent):
    def __init__(self, unique_id, model, is_occupied: bool = False):
        super().__init__(unique_id, model)
        self.is_apartado = False
        self.is_occupied = is_occupied