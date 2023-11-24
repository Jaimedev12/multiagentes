from mesa.agent import Agent    

class ShippingShelf(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.is_apartado = False
        self.is_occupied = False