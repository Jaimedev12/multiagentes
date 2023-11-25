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
from step_actions.fullfill_shipping_orders import fullfill_shipping_orders
from step_actions.spawn_box import spawn_box

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

        # Posicionando las cintas transportadoras
        #conveyor_belt_positions = [(8, 19), (8, 18), (6, 19), (6, 18), (0, 16), (1, 16), (2, 16), (3, 16), (4, 16), (5, 16), (6, 16), (7, 16), (8, 16), (9, 16), (10, 16), (11, 16), (12, 16), (13, 16), (14, 16), (15, 16), (16, 16), (17, 16)]
        conveyor_belt_positions = [(8, 19, True), (8, 18, False), (6, 19, True), (6, 18, False)]
        for i, pos in enumerate(conveyor_belt_positions):
            conveyor_belt = ConveyorBelt("5"+str(i), self, direction=(0, -1), is_spawn_point=pos[2])
            self.grid.place_agent(conveyor_belt, (pos[0], pos[1]))
            available_positions.remove((pos[0], pos[1]))
        # Posicionando estantes de recolección
        collection_shelf_positions = [(8, 17), (6, 17)]
        for i, pos in enumerate(collection_shelf_positions):
            shelf = Shelf("2"+str(i), self, is_storage=False)
            self.grid.place_agent(shelf, pos)
            available_positions.remove(pos)

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
            model_reporters={"AgentActions": get_agent_actions, "OutBoxesNeeded": lambda model: model.out_boxes_needed},
        )

    def remove_agent(self, agent):
        self.grid.remove_agent(agent)

    def step(self):
        spawn_box(self)
        fullfill_shipping_orders(self)
        assign_robots_to_boxes_needing_storage(self)
        assign_actions_to_robots_needing_charge(self)
        
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

