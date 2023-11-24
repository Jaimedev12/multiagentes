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

from .utils import find_closest_agent, move_out_of_the_way

def assign_robots_to_boxes_needing_storage(model: Model):
    boxes_to_store = get_boxes_to_store(model)

    for box in boxes_to_store:
        closest_robot = get_closest_robot(box, model)
        if closest_robot == 0: 
            continue

        if assign_box_to_robot(box, closest_robot, model) == False:
            closest_robot.objectives_assigned = list()
            continue
        
        if assign_shelf_to_robot(closest_robot, model) == False:
            box.is_apartada = False
            closest_robot.objectives_assigned = list()
            continue

        if move_out_of_the_way(closest_robot, model) == False:
            closest_robot.objectives_assigned = list()
            continue


def get_boxes_to_store(model: Model) -> list:
    boxes_to_store = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Box) and obj.is_apartada == False:
                boxes_to_store.append(obj)
    
    return boxes_to_store

def get_closest_robot(box: Box, model: Model):
    closest_robot = find_closest_agent(
        start_pos=box.pos,
        is_target=lambda agent: isinstance(agent, Robot) and len(agent.objectives_assigned) == 0,
        is_not_valid=lambda agent: isinstance(agent, ChargingStation) or 
                                   isinstance(agent, ConveyorBelt),
        model=model
        )

    return closest_robot

def assign_box_to_robot(box: Box, robot: Robot, model: Model) -> bool:    
    box.is_apartada = True
    robot.objectives_assigned.append((box.pos, lambda robot: robot.lift_box()))

    return True

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
