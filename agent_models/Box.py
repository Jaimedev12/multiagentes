from mesa.agent import Agent

from agent_models.Cell import Cell
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf
from agent_models.ConveyorBelt import ConveyorBelt

from response_format.ActionType import ActionType
from response_format.AgentAction import AgentAction
from response_format.GridPosition import GridPosition

class Box(Agent):
    def __init__(self, unique_id, model, just_spawned=False):
        super().__init__(unique_id, model)
        self.is_apartada = False
        self.sig_pos = None
        self.is_ready_to_pick_up = False
        self.just_spawned = just_spawned

        self.cur_action_type = None
        self.cur_agent_action = None
    
    def step(self):
        if self.just_spawned:
            self.just_spawned = False
            self.dont_move()
            self.cur_action_type = ActionType.SPAWN
            return

        conveyor_belt = self.get_conveyor_belt()
        if conveyor_belt == 0: 
            self.dont_move()
            return
        
        if self.is_box_in_next_pos(conveyor_belt):
            self.dont_move()
            return

        self.move(direction=conveyor_belt.direction)

        collection_shelf = self.get_collection_shelf()
        if collection_shelf != 0:
            collection_shelf.is_occupied = True
            self.is_ready_to_pick_up = True
            return
        
    def advance(self):
        self.cur_agent_action = self.get_action()
        self.model.grid.move_agent(self, self.sig_pos)
        self.cur_action_type = None

    def get_action(self):
        print("cur_ action type: ", self.cur_action_type)
        return AgentAction(_from=GridPosition(self.pos[0], self.pos[1]), _to=GridPosition(self.sig_pos[0], self.sig_pos[1]), _type=self.cur_action_type)


    def dont_move(self):
        self.sig_pos = self.pos

    def move(self, direction: tuple):
        next_pos = (self.pos[0] + direction[0], self.pos[1] + direction[1])
        self.sig_pos = next_pos
        self.cur_action_type = ActionType.MOVE

    def get_collection_shelf(self):
        agents = self.model.grid.get_cell_list_contents([self.sig_pos])
        for agent in agents:
            if isinstance(agent, Shelf) and not agent.is_storage:
                return agent
        return 0

    def is_box_in_next_pos(self, conveyor_belt: ConveyorBelt):
        next_pos = (self.pos[0] + conveyor_belt.direction[0], self.pos[1] + conveyor_belt.direction[1])
        agents = self.model.grid.get_cell_list_contents([next_pos])
        for agent in agents:
            if isinstance(agent, Box):
                return True
        return False
    
    def get_conveyor_belt(self):
        agents = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents:
            if isinstance(agent, ConveyorBelt):
                return agent
        return 0