import random

from mesa.model import Model

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf
from agent_models.ConveyorBelt import ConveyorBelt
from agent_models.ShippingShelf import ShippingShelf

def spawn_box(model: Model):
    current_step = model.schedule.steps
    if current_step % (60//model.in_boxes_per_minute) != 0:
        return

    available_positions = get_available_spawning_positions(model)   
    if len(available_positions) == 0:
        print('No hay posiciones disponibles para spawnear una caja')
        return

    instantiate_box(model, available_positions[0])

def get_available_spawning_positions(model: Model):
    available_positions = list()
    for cell in model.grid.coord_iter():
        cell_content, pos = cell

        is_invalid = False
        for obj in cell_content:
            if isinstance(obj, Box):
                is_invalid = True
                break

        if is_invalid:
            continue

        for obj in cell_content:
            if isinstance(obj, ConveyorBelt) and obj.is_spawn_point:
                available_positions.append(obj.pos)
    
    return available_positions

def instantiate_box(model: Model, pos: tuple):
    num_steps = model.schedule.steps
    box = Box(str(num_steps)+'a', model)
    model.grid.place_agent(box, pos)
    model.schedule.add(box)
