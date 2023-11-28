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
    
        # Movement restrictions to force exit direction ------------------------
        restricted_positions = set()
        agents_in_current_pos = model.grid.get_cell_list_contents([cur_pos])
        for agent in agents_in_current_pos:
            if not hasattr(agent, 'not_allowed_movement_positions') or \
                agent.not_allowed_movement_positions is None:
                continue
            for not_allowed_pos in agent.not_allowed_movement_positions:
                pos = (cur_pos[0] + not_allowed_pos[0], cur_pos[1] + not_allowed_pos[1])
                restricted_positions.add(pos)
        # ------
            
        for pos in neighbor_positions:
            if pos in restricted_positions:
                continue

            agents_in_neighbor_pos = model.grid.get_cell_list_contents([pos])

            # Movement restrictions to force exit direction ------------------------
            is_restricted = False
            for agent in agents_in_neighbor_pos:
                if not hasattr(agent, 'not_allowed_movement_positions') or \
                    agent.not_allowed_movement_positions is None:
                    continue
                for not_allowed_pos in agent.not_allowed_movement_positions:
                    new_pos = (pos[0] + not_allowed_pos[0], pos[1] + not_allowed_pos[1])
                    if new_pos == cur_pos:
                        is_restricted = True
                        break
            if is_restricted:
                continue
            # ------

            for agent in agents_in_neighbor_pos:                
                if is_not_valid(agent):
                    is_restricted = True
                    break
            if is_restricted:
                continue

            for agent in agents_in_neighbor_pos:
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

def get_distance(pos1, pos2):
    return abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1])