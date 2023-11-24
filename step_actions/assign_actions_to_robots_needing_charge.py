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

def assign_actions_to_robots_needing_charge(model: Model):
    robots_needing_charge = get_robots_needing_charge(model)
    for robot in robots_needing_charge:
        if assign_charge_station(robot, model) == False:
            robot.objectives_assigned = list()
            continue

        if move_out_of_the_way(robot, model) == False:
            robot.objectives_assigned = list()
            continue

def get_robots_needing_charge(model: Model) -> list:

    min_charge_allowed = 60
    robots_needing_charge = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Robot) and obj.cur_charge <= min_charge_allowed and len(obj.objectives_assigned) == 0:
                robots_needing_charge.append(obj)
    
    return robots_needing_charge


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

    #closest_charging_station.is_apartada = True

    return True