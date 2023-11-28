from mesa.agent import Agent    

class ChargingStation(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_apartada = False
        self.not_allowed_movement_positions = [(-1, -1), (-1, 1), (1, -1), (1, 1)] # Diagonals