from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf

from collections import deque

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
        box = Box(1, self)
        self.grid.place_agent(box, box_position)
        available_positions.remove(box_position)

        # Posicionamiento de la estación de carga
        charge_station_position = (0, 0)
        charge_station = ChargingStation(2, self)
        self.grid.place_agent(charge_station, charge_station_position)
        available_positions.remove(charge_station_position)

        # Posicionando los estantes
        for i in range(8, 12, 2):
            shelf_position = (0, i+1)
            shelf = Shelf("3"+str(i), self)
            self.grid.place_agent(shelf, shelf_position)
            available_positions.remove(shelf_position)

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

    def step(self):
        robots_needing_charge = get_robots_needing_charge(self)
        # boxes_to_store = get_boxes_to_store(self)
        # boxes_to_ship = get_boxes_to_ship(self)

        for robot in robots_needing_charge:

            def when_arrives_at_charging_station(robot: Robot):
                robot.is_charging = True

            if assign_charge_station(robot, when_arrives_at_charging_station, self) == False:
                continue

            def when_arrive_at_resting_place(robot: Robot):
                robot.target_position = None
                robot.dont_move()

            assign_resting_place(robot, when_arrive_at_resting_place, self) # Para que no se quede en la estación de carga

        # for box in boxes_to_store:
        #     robot = find_closest_robot(box, self)
        #     assign_box_to_robot(robot, box, self)
        #     assign_shelf_to_robot(robot, self)

        # for box in boxes_to_ship:
        #     robot = find_closest_robot(box, self)
        #     assign_box_to_robot(robot, box, self)
        #     assign_shelf_to_robot(robot, self)


        self.datacollector.collect(self)
        self.schedule.step()

def assign_shelf_to_robot(robot: Robot, model: Model):
    ...

def assign_box_to_robot(robot: Robot, box: Box, model: Model):
    ...

def find_closest_robot(box: Box, model: Model) -> Robot:
    ...



def assign_charge_station(robot: Robot, action, model: Model):
    closest_charging_station_pos = find_closest_tile(robot, 
            start_pos=robot.pos,
            is_target=lambda agent: isinstance(agent, ChargingStation) and agent.is_apartada == False, 
            is_valid=lambda agent: isinstance(agent, Cell), 
            model=model)

    if closest_charging_station_pos == 0:
        return False
    
    robot.objectives_assigned.append((closest_charging_station_pos, action))

    agents_in_pos = model.grid.get_cell_list_contents([closest_charging_station_pos])
    charging_stations = list(filter(lambda agent: isinstance(agent, ChargingStation), agents_in_pos))
    for station in charging_stations: # Solo debería haber uno
        station.is_apartada = True

    return True

def assign_resting_place(robot: Robot, action, model: Model):
    closest_valid_pos = find_closest_tile(robot, 
            start_pos=robot.objectives_assigned[0][0],
            is_target=lambda agent: isinstance(agent, Cell) and agent.is_apartada == False, 
            is_valid=lambda agent: isinstance(agent, Cell), 
            model=model)

    if closest_valid_pos == 0:
        raise Exception("No hay celdas disponibles, error inesperado")

    robot.objectives_assigned.append((closest_valid_pos, action))
    return True



def get_agent_actions(model: Model) -> list:
    agent_actions = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_agent_action != None:
                agent_actions.append(obj.cur_agent_action)
                obj.cur_agent_action = None
    
    return agent_actions

def get_robots_needing_charge(model: Model) -> list:
    robots_needing_charge = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_charge <= 40 and len(obj.objectives_assigned) == 0:
                robots_needing_charge.append(obj)
    
    return robots_needing_charge

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
            if isinstance(obj, Box) and obj.is_stored == True and obj.is_apartada == False:
                boxes_to_ship.append(obj)
    
    return boxes_to_ship


def find_closest_tile(self, start_pos, is_target, is_valid, model: Model):
    queue = deque()
    queue.append(start_pos)
    visited = dict()

    while queue:
        cur_pos = queue.popleft()

        if cur_pos in visited:
            continue

        visited[cur_pos] = True
        neighbors = model.grid.get_neighbors(
            cur_pos, moore=True, include_center=False)

        for agent in neighbors:
            if is_target(agent):
                return agent.pos

            if is_valid(agent):
                queue.append(agent.pos)

    return 0

