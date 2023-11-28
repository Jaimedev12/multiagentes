from mesa.agent import Agent    

class Shelf(Agent):
    def __init__(self, unique_id, model, is_storage: bool = True):
        super().__init__(unique_id, model)
        self.is_apartado = False
        self.is_occupied = False
        self.is_storage = is_storage
        self.not_allowed_movement_positions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Diagonals