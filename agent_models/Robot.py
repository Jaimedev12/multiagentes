from mesa.agent import Agent
from collections import deque
import math

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf
from agent_models.ConveyorBelt import ConveyorBelt

from response_format.ActionType import ActionType
from response_format.AgentAction import AgentAction
from response_format.GridPosition import GridPosition

class Robot(Agent):

    max_charge = 100
    charge_rate = 25

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.cur_charge = self.max_charge

        self.target_position = None
        self.objectives_assigned = list()
        self.current_objective = 0

        self.current_path_visited_dict = dict()
        self.is_charging = False
        self.is_lifting_box = False

        self.cur_movement_positions_apartadas = list()

        # Response variables
        self.cur_action_type = None
        self.cur_agent_action = None

        # Estadísticas
        self.movements = 0
        self.num_recharges = 0

    def calc_dist(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def dont_move(self):
        self.sig_pos = self.pos

    def order_neighbors_by_distance(self, neighbors, posicion_destino):
        distances = []
        for pos in neighbors:
            pos_with_distance = (self.calc_dist(pos, posicion_destino), pos)
            distances.append(pos_with_distance)

        distances.sort(key=lambda x: x[0])

        for i in range(len(neighbors)):
            neighbors[i] = distances[i][1]

        return neighbors

    def apartar_movement_positions(self, sig_pos):
        self.cur_movement_positions_apartadas.append(sig_pos)
        if sig_pos[0] != self.pos[0]:
            self.cur_movement_positions_apartadas.append((sig_pos[0], self.pos[1]))
            self.cur_movement_positions_apartadas.append((self.pos[0], sig_pos[1]))

        for pos in self.cur_movement_positions_apartadas:
            agentes_en_pos = self.model.grid.get_cell_list_contents([pos])
            celda_en_pos = list(filter(lambda agente : isinstance(agente, Cell), agentes_en_pos))[0]
            celda_en_pos.is_apartada = True

    def apartar_single_position(self, pos):
        agentes_en_pos = self.model.grid.get_cell_list_contents([pos])
        celda_en_pos = list(filter(lambda agente : isinstance(agente, Cell), agentes_en_pos))[0]
        celda_en_pos.is_apartada = True

    def free_movement_positions(self):
        for pos in self.cur_movement_positions_apartadas:
            agentes_en_pos = self.model.grid.get_cell_list_contents([pos])
            celda_en_pos = list(filter(lambda agente : isinstance(agente, Cell), agentes_en_pos))[0]
            celda_en_pos.is_apartada = False
        self.cur_movement_positions_apartadas = list()

    def pick_box_from_collection_shelf(self):
        self.is_lifting_box = True
        self.cur_action_type = ActionType.PICK
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        box_to_remove = list(filter(lambda agent: isinstance(agent, Box), agents_in_pos))[0]
        self.model.remove_agent(box_to_remove)
        self.model.schedule.remove(box_to_remove)
        
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        shelf = list(filter(lambda agent: isinstance(agent, Shelf), agents_in_pos))[0]
        shelf.is_occupied = False

    def store_box(self):
        self.is_lifting_box = False
        self.cur_action_type = ActionType.DROP
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        shelf = list(filter(lambda agent: isinstance(agent, Shelf), agents_in_pos))[0]
        shelf.is_occupied = True
        shelf.is_apartado = False

    def take_box_from_storage(self):
        self.is_lifting_box = True
        self.cur_action_type = ActionType.PICK
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        shelf = list(filter(lambda agent: isinstance(agent, Shelf), agents_in_pos))[0]
        shelf.is_occupied = False
        shelf.is_apartado = False

    def ship_box(self):
        self.is_lifting_box = False
        self.cur_action_type = ActionType.DROP
        self.model.shipment_orders_pending -= 1
        self.model.shipped_orders += 1

    def charge(self):
        self.cur_charge = min(self.cur_charge+self.charge_rate, self.max_charge)
        self.cur_action_type = ActionType.CHARGE

        if self.cur_charge == self.max_charge:
            self.is_charging = False
            self.num_recharges += 1

            agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
            charging_station = list(filter(lambda agent: isinstance(agent, ChargingStation), agents_in_pos))[0]
            charging_station.is_apartada = False

    def get_valid_neighbors(self):
        neighbor_agents = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        # Marcar posiciones bloqueadas
        blocked_positions = set()
        for agent in neighbor_agents:
            if (isinstance(agent, (Robot))
                    # or (agent.pos in self.current_path_visited_dict) # Ya se visitó en el recorrido actual
                    or (isinstance(agent, Cell) and agent.is_apartada) # Ya está apartada la celda
                    or (self.is_lifting_box and isinstance(agent, Shelf) and agent.is_occupied) # No se puede pasar por un estante ocupado mientras se carga una caja           
                    or (isinstance(agent, ConveyorBelt))): #
                blocked_positions.add(agent.pos)

        neighbor_positions = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)
        
        restricted_positions = set()
        # Movement restrictions to force entry direction ------------------------
        for pos in neighbor_positions:
            position_difference = (pos[0] - self.pos[0], pos[1] - self.pos[1])
            agents_in_neighbor_pos = self.model.grid.get_cell_list_contents([pos])

            for agent in agents_in_neighbor_pos:
                if not hasattr(agent, 'not_allowed_movement_positions') or \
                   agent.not_allowed_movement_positions is None:
                    continue

                if position_difference in agent.not_allowed_movement_positions:
                    restricted_positions.add(pos)
                    break
                 
        # Movement restrictions to force exit direction --------------------------
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        for agent in agents_in_pos:
            if not hasattr(agent, 'not_allowed_movement_positions') or \
                agent.not_allowed_movement_positions is None:
                continue
            for not_allowed_pos in agent.not_allowed_movement_positions:
                pos = (self.pos[0] + not_allowed_pos[0], self.pos[1] + not_allowed_pos[1])
                restricted_positions.add(pos)

        allowed_positions = [pos for pos in neighbor_positions if pos not in blocked_positions and pos not in restricted_positions]
        return allowed_positions


    def move_to_target_position(self):
        allowed_positions = self.get_valid_neighbors()
        print("Number of allowed positions: ", len(allowed_positions))
        print("allowed positions: ", allowed_positions)

        if len(allowed_positions) == 0:
            self.dont_move()
            return
        
        neighbors_by_distance = self.order_neighbors_by_distance(allowed_positions, self.target_position)
        self.sig_pos = neighbors_by_distance[0]
        self.apartar_movement_positions(self.sig_pos)


    def step(self):
        # print("objetivos: ", len(self.objectives_assigned))
        # print("objetivo actual: ", self.current_objective)
        # print("is charging: ", self.is_charging)
        # print("target position: ", self.target_position)

        if self.cur_charge <= 0:
            self.dont_move()
            return
        
        if self.is_charging and self.cur_charge < self.max_charge:
            self.charge()
            self.dont_move()
            return
        
        if len(self.objectives_assigned) == self.current_objective:
            self.objectives_assigned = list()
            self.current_objective = 0
            self.has_target_cell = False
            self.dont_move()
            return
        
        if self.pos == self.objectives_assigned[self.current_objective][0]:
            # Ejecuta la acción del objetivo
            self.objectives_assigned[self.current_objective][1](self)

            self.current_objective += 1
            self.current_path_visited_dict = dict()
            self.dont_move()
            return
        
        if len(self.objectives_assigned) > 0:
            self.target_position = self.objectives_assigned[self.current_objective][0]

        self.move_to_target_position()

    def get_action(self) -> AgentAction:
        if self.cur_action_type == None:
            self.cur_action_type = ActionType.MOVE

        return AgentAction(_from=GridPosition(self.pos[0], self.pos[1]), _to=GridPosition(self.sig_pos[0], self.sig_pos[1]), _type=self.cur_action_type)

    def advance(self):
        self.cur_agent_action = self.get_action()
        self.cur_action_type = None
        
        if self.pos != self.sig_pos:
            self.free_movement_positions()
            self.apartar_single_position(self.sig_pos)
            self.current_path_visited_dict[self.pos] = True
            self.cur_movement_positions_apartadas.append(self.sig_pos)
            self.movements += 1  
            self.cur_charge -= 1  
        # else :
            # self.cur_charge -= 0.1
        
        self.cur_charge = max(self.cur_charge, 0)

        self.model.grid.move_agent(self, self.sig_pos)
