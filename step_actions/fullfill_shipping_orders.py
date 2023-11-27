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

from .utils import get_distance, find_closest_agent, move_out_of_the_way

def fullfill_shipping_orders(model: Model):
    update_shipping_orders(model)
    if model.shipment_orders_pending <= 0:
        return
    
    for i in range(0, model.out_boxes_pending_assigment):
        (shipping_shelf, occupied_shelf) = find_closest_ShippingShelf_OccupiedShelf_pair(model)
        if shipping_shelf == 0 or occupied_shelf == 0:
            break

        closest_robot = find_closest_robot_from_shelf(occupied_shelf, model)
        if closest_robot == 0:
            break

        if assign_occupied_shelf_to_robot(occupied_shelf, closest_robot, model) == False:
            break
        
        if assign_shipping_shelf_to_robot(shipping_shelf, closest_robot, model) == False:
            closest_robot.objectives_assigned = list()
            occupied_shelf.is_apartado = False
            break

        if assign_move_out_of_the_way_action(closest_robot, model) == False:
            closest_robot.objectives_assigned = list()
            occupied_shelf.is_apartado = False
            break

        model.out_boxes_pending_assigment -= 1

        # if move_out_of_the_way(closest_robot, model) == False:
        #     closest_robot.objectives_assigned = list()
        #     occupied_shelf.is_apartado = False
        #     break

def assign_shipping_shelf_to_robot(shipping_shelf: ShippingShelf, robot: Robot, model: Model):
    robot.objectives_assigned.append((shipping_shelf.pos, lambda robot: robot.ship_box()))
    return True

def assign_occupied_shelf_to_robot(occupied_shelf: Shelf, robot: Robot, model: Model):
    occupied_shelf.is_apartado = True
    robot.objectives_assigned.append((occupied_shelf.pos, lambda robot: robot.take_box_from_storage()))

    return True
    
def assign_move_out_of_the_way_action(robot: Robot, model: Model) :
    robot.objectives_assigned.append((robot.objectives_assigned[len(robot.objectives_assigned)-1][0], lambda robot: move_out_of_the_way(robot, robot.model)))

def find_closest_robot_from_shelf(shelf: Shelf, model: Model):
    closest_robot = find_closest_agent( 
            start_pos=shelf.pos,
            is_target=lambda agent: isinstance(agent, Robot) and len(agent.objectives_assigned) == 0, 
            is_not_valid=lambda agent: isinstance(agent, Robot) and len(agent.objectives_assigned) > 0 or 
                                       isinstance(agent, ConveyorBelt),
            model=model)
    return closest_robot
    
def find_closest_ShippingShelf_OccupiedShelf_pair(model: Model):
    shipping_shelves = get_shipping_shelves(model)
    occupied_shelves = get_occupied_shelves(model)

    closest_pair = (0, 0)
    closest_distance = 10000

    for shipping_shelf in shipping_shelves:
        for occupied_shelf in occupied_shelves:
            distance = get_distance(shipping_shelf.pos, occupied_shelf.pos)
            if distance < closest_distance:
                closest_pair = (shipping_shelf, occupied_shelf)
                closest_distance = distance

    return closest_pair

def update_shipping_orders(model: Model):
    current_step = model.schedule.steps
    if current_step % (60//model.out_boxes_per_minute) == 0:
        model.out_boxes_pending_assigment += 1
        model.shipment_orders_pending += 1

def get_occupied_shelves(model: Model) -> list:
    occupied_shelves = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell
        for obj in cell_content:
            if isinstance(obj, Shelf) and obj.is_occupied == True and obj.is_apartado == False and obj.is_storage:
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


