# import random

from mesa.model import Model
# from mesa.space import MultiGrid
# from mesa.time import SimultaneousActivation
# from mesa.datacollection import DataCollector

from agent_models.Cell import Cell
# from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.ChargingStation import ChargingStation
# from agent_models.Shelf import Shelf
from agent_models.ConveyorBelt import ConveyorBelt
# from agent_models.ShippingShelf import ShippingShelf

from collections import deque

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