import random

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
from agent_models.ShippingShelf import ShippingShelf

from collections import deque

from step_actions.utils import find_closest_agent, move_out_of_the_way
from step_actions.assign_actions_to_robots_needing_charge import assign_actions_to_robots_needing_charge
from step_actions.assign_robots_to_boxes_needing_storage import assign_robots_to_boxes_needing_storage

class Room(Model):
    def __init__(self, M: int = 20, N: int = 20,
                 num_robots: int = 1,
                 modo_pos_inicial: str = 'Aleatoria',
                 in_boxes_per_minute: int = 1,
                 out_boxes_per_minute: int = 1
                 ):

        super().__init__()
        self.current_id = 0

        self.num_robots = num_robots
        self.in_boxes_per_minute = in_boxes_per_minute
        self.out_boxes_per_minute = out_boxes_per_minute
        
        self.out_boxes_needed = 0

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        available_positions = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de celdas
        for id, pos in enumerate(available_positions):
            cell = Cell(int(f"{num_robots}{id}") + 1, self)
            self.grid.place_agent(cell, pos)

        # Posicionamiento de la estación de carga
        charge_station_position = (0, 0)
        charge_station = ChargingStation(20, self)
        self.grid.place_agent(charge_station, charge_station_position)
        available_positions.remove(charge_station_position)

        charge_station_position = (0, 19)
        charge_station = ChargingStation(21, self)
        self.grid.place_agent(charge_station, charge_station_position)
        available_positions.remove(charge_station_position)

        # Posicionando los estantes
        for i in range(4, 15, 2):
            shelf_position = (0, i+1)
            shelf = Shelf("3"+str(i), self)
            self.grid.place_agent(shelf, shelf_position)
            available_positions.remove(shelf_position)

        # Posicionando los estantes de salida
        for i in range(5, 15, 8):
            shelf_position = (19, i+1)
            shelf = ShippingShelf("4"+str(i), self)
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
        # fullfill_shipping_orders(self)

        current_step = self.schedule.steps
        if current_step % (60//self.in_boxes_per_minute) == 0:
            instantiate_box(self)

        self.datacollector.collect(self)
        self.schedule.step()

def instantiate_box(model: Model):
    box_position = (random.randint(5, 15), random.randint(5, 15))
    uuid = model.schedule.steps
    box = Box(uuid*2, model)
    model.grid.place_agent(box, box_position)


def fullfill_shipping_orders(model: Model):
    update_shipping_orders(model)
    if model.out_boxes_needed == 0:
        return
    
    for i in range(0, model.out_boxes_needed):
        (shipping_shelf, occupied_shelf) = find_closest_ShippingShelf_OccupiedShelf_pair(model)
        closest_robot = find_closest_robot_from_shelf(occupied_shelf, model)

        if assign_occupied_shelf_to_robot(occupied_shelf, closest_robot, model) == False:
            print("No se pudo asignar estante ocupado a robot")
            break
        
        if assign_shipping_shelf_to_robot(shipping_shelf, closest_robot, model) == False:
            print("No se pudo asignar estante de salida a robot")
            break

def assign_shipping_shelf_to_robot(shipping_shelf: ShippingShelf, robot: Robot, model: Model):
    ...

def assign_occupied_shelf_to_robot(occupied_shelf: Shelf, robot: Robot, model: Model):
    ...

def find_closest_robot_from_shelf(shelf: Shelf, model: Model):
    ...    

def find_closest_ShippingShelf_OccupiedShelf_pair(model: Model):
    shipping_shelves = get_shipping_shelves(model)
    occupied_shelves = get_occupied_shelves(model)

    closest_pair = (0, 0)
    closest_distance = 10000

    for shipping_shelf in shipping_shelves:
        for occupied_shelf in occupied_shelves:
            distance = model.grid.get_distance(shipping_shelf.pos, occupied_shelf.pos)
            if distance < closest_distance:
                closest_pair = (shipping_shelf, occupied_shelf)
                closest_distance = distance

    return closest_pair


def update_shipping_orders(model: Model):
    current_step = model.schedule.steps
    if current_step % (60//model.out_boxes_per_minute) == 0:
        model.out_boxes_needed += 1

def get_agent_actions(model: Model) -> list:
    agent_actions = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_agent_action != None:
                agent_actions.append(obj.cur_agent_action)
                obj.cur_agent_action = None
    
    return agent_actions


def get_occupied_shelves(model: Model) -> list:
    occupied_shelves = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Shelf) and obj.is_occupied == True:
                occupied_shelves.append(obj)
    
    return occupied_shelves

def get_shipping_shelves(model: Model) -> list:
    shipping_shelves = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, ShippingShelf):
                shipping_shelves.append(obj)
    
    return shipping_shelves

