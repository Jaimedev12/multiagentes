from mesa.agent import Agent    

class ChargingStation(Agent):
    def __init__(self, unique_id, model, is_occupied: bool = False):
        super().__init__(unique_id, model)
        self.is_occupied = is_occupied