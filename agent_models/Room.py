from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot

class Room(Model):
    def __init__(self, M: int = 20, N: int = 20,
                 num_robots: int = 1,
                 modo_pos_inicial: str = 'Aleatoria',
                 ):

        super().__init__()
        self.current_id = 0

        self.num_robots = num_robots

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        available_positions = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de celdas
        for id, pos in enumerate(available_positions):
            cell = Cell(int(f"{num_robots}{id}") + 1, self)
            self.grid.place_agent(cell, pos)

        # Posicionamiento de la caja
        box_position = (N//2, M//2)
        box = Box(1234562341, self)
        self.grid.place_agent(box, box_position)
        available_positions.remove(box_position)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            start_pos_robots = self.random.sample(available_positions, k=num_robots)
        else:  # 'Fija'
            start_pos_robots = [(1, 1)] * num_robots

        for id in range(num_robots):
            robot = Robot(id, self)
            self.grid.place_agent(robot, start_pos_robots[id])
            self.schedule.add(robot)

        self.datacollector = DataCollector(
            model_reporters={"AgentActions": get_agent_actions},
        )

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def step(self):

        agents_needing_charge = get_agents_needing_charge(self)
        boxes_to_store = get_boxes_to_store(self)
        boxes_to_ship = get_boxes_to_ship(self)

        print("Boxes to store: ", len(boxes_to_store))

        self.datacollector.collect(self)
        self.schedule.step()

def get_agent_actions(model: Model) -> list:
    agent_actions = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_agent_action != None:
                agent_actions.append(obj.cur_agent_action)
                obj.cur_agent_action = None
    
    return agent_actions

def get_agents_needing_charge(model: Model) -> list:
    agents_needing_charge = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_charge <= 40 and obj.has_target_cell == False:
                agents_needing_charge.append(obj)
    
    return agents_needing_charge

def get_boxes_to_store(model: Model) -> list:
    boxes_to_store = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Box) and obj.is_stored == False and obj.is_being_carried == False and obj.is_apartada == False:
                boxes_to_store.append(obj)
    
    return boxes_to_store

def get_boxes_to_ship(model: Model) -> list:
    boxes_to_ship = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Box) and obj.is_stored == True == False and obj.is_apartada == False:
                boxes_to_ship.append(obj)
    
    return boxes_to_ship


