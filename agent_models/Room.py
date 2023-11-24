from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf
from agent_models.ConveyorBelt import ConveyorBelt

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

    def remove_agent(self, agent):
        self.grid.remove_agent(agent)

    def step(self):
        assign_actions_to_robots_needing_charge(self)
        assign_robots_to_boxes_needing_storage(self)

        self.datacollector.collect(self)
        self.schedule.step()

def assign_robots_to_boxes_needing_storage(model: Model):
    boxes_to_store = get_boxes_to_store(model)

    # for box in boxes_to_store:
    #     print("Caja en pos: ", box.pos)

    for box in boxes_to_store:
        closest_robot = get_closest_robot(box, model)
    
        if closest_robot == 0: 
            print("No se encontró robot")
            continue

        print("Robot en pos: ", closest_robot.pos)

        if assign_box_to_robot(box, closest_robot, model) == False: 
            print("No se pudo asignar caja a robot")
            closest_robot.objectives_assigned = list()
            continue
        
        if assign_shelf_to_robot(closest_robot, model) == False: 
            print("No se pudo asignar estante a robot")
            closest_robot.objectives_assigned = list()
            continue

        if move_out_of_the_way(closest_robot, model) == False: 
            print("No se pudo mover robot")
            closest_robot.objectives_assigned = list()
            continue

def assign_actions_to_robots_needing_charge(model: Model):
    robots_needing_charge = get_robots_needing_charge(model)
    for robot in robots_needing_charge:
        if assign_charge_station(robot, model) == False:
            print("No se pudo asignar estación de carga")
            robot.objectives_assigned = list()
            continue

        if move_out_of_the_way(robot, model) == False:
            print("No se pudo mover robot")
            robot.objectives_assigned = list()
            continue

def assign_shelf_to_robot(robot: Robot, model: Model):
    closest_shelf = find_closest_agent(
        start_pos=robot.pos,
        is_target=lambda agent: isinstance(agent, Shelf) and agent.is_apartado == False and agent.is_occupied == False,
        is_not_valid=lambda agent: isinstance(agent, Robot) or 
                                   (isinstance(agent, Shelf) and agent.is_occupied) or
                                   isinstance(agent, ChargingStation) or 
                                   isinstance(agent, ConveyorBelt),
        model=model
        )
    
    if closest_shelf == 0:
        return False
    
    closest_shelf.is_apartado = True
    robot.objectives_assigned.append((closest_shelf.pos, lambda robot: robot.store_box()))

def assign_box_to_robot(box: Box, robot: Robot, model: Model) -> bool:    
    box.is_apartada = True
    robot.objectives_assigned.append((box.pos, lambda robot: robot.lift_box()))

    return True

def get_closest_robot(box: Box, model: Model):
    closest_robot = find_closest_agent(
        start_pos=box.pos,
        is_target=lambda agent: isinstance(agent, Robot) and len(agent.objectives_assigned) == 0,
        is_not_valid=lambda agent: isinstance(agent, ChargingStation) or 
                                   isinstance(agent, ConveyorBelt),
        model=model
        )

    return closest_robot



def assign_charge_station(robot: Robot, model: Model):
    closest_charging_station = find_closest_agent( 
            start_pos=robot.pos,
            is_target=lambda agent: isinstance(agent, ChargingStation) and agent.is_apartada == False, 
            is_not_valid=lambda agent: isinstance(agent, Robot) or 
                                       isinstance(agent, ConveyorBelt),
            model=model)

    if closest_charging_station == 0:
        return False
    
    def when_arrives(robot: Robot):
        robot.is_charging = True

    robot.objectives_assigned.append((closest_charging_station.pos, when_arrives))

    closest_charging_station.is_apartada = True

    return True

def move_out_of_the_way(robot: Robot, model: Model):
    closest_valid_cell = find_closest_agent(
            start_pos=robot.objectives_assigned[len(robot.objectives_assigned)-1][0],
            is_target=lambda agent: isinstance(agent, Cell) and agent.is_apartada == False,
            is_not_valid=lambda agent: isinstance(agent, Robot) or 
                                       isinstance(agent, ChargingStation) or 
                                       isinstance(agent, ConveyorBelt),
            model=model)

    if closest_valid_cell == 0:
        return False

    def when_arrives(robot: Robot):
        robot.target_position = None
        robot.dont_move()

    robot.objectives_assigned.append((closest_valid_cell.pos, when_arrives))
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


def find_closest_agent(start_pos, is_target, is_not_valid, model: Model):
    queue = deque()
    queue.append(start_pos)
    visited = dict()

    while queue:
        cur_pos = queue.popleft()

        if cur_pos in visited:
            continue

        visited[cur_pos] = True

        neighbor_positions = model.grid.get_neighborhood(
            cur_pos, moore=True, include_center=False)
        
        for pos in neighbor_positions:
            agents = model.grid.get_cell_list_contents([pos])
            for agent in agents:                
                if is_not_valid(agent):
                    break

                if is_target(agent):
                    return agent
                
                queue.append(agent.pos)

    return 0

