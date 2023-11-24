from mesa.agent import Agent
from collections import deque

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf

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

        # Response variables
        self.cur_action_type = None
        self.cur_agent_action = None

        # Estadísticas
        self.movements = 0
        self.num_recharges = 0

    def calc_dist(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

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

    def apartar_pos(self, pos):
        agentes_en_pos = self.model.grid.get_cell_list_contents([pos])
        celda_en_pos = filter(lambda agente : isinstance(agente, Cell), agentes_en_pos)
        for celda in celda_en_pos:
            celda.is_apartada = True

    def free_pos(self, pos):
        agentes_en_pos = self.model.grid.get_cell_list_contents([pos])
        celda_en_pos = filter(lambda agente : isinstance(agente, Cell), agentes_en_pos)
        for celda in celda_en_pos:
            celda.is_apartada = False

    def lift_box(self):
        self.is_lifting_box = True
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        box_to_remove = list(filter(lambda agent: isinstance(agent, Box), agents_in_pos))[0]
        self.model.remove_agent(box_to_remove)

    def store_box(self):
        self.is_lifting_box = False
        agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
        shelf = list(filter(lambda agent: isinstance(agent, Shelf), agents_in_pos))[0]
        shelf.is_occupied = True
        shelf.is_apartado = False

    def charge(self):
        self.cur_charge = min(self.cur_charge+self.charge_rate, self.max_charge)
        self.cur_action_type = ActionType.CHARGE

        if self.cur_charge == self.max_charge:
            self.is_charging = False
            self.num_recharges += 1

            agents_in_pos = self.model.grid.get_cell_list_contents([self.pos])
            charging_stations = list(filter(lambda agent: isinstance(agent, ChargingStation), agents_in_pos))
            for station in charging_stations: # Solo debería haber uno
                station.is_apartada = False

    def get_valid_neighbors(self):
        neighbor_agents = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        # Marcar posiciones bloqueadas
        blocked_positions = set()
        for cell in neighbor_agents:
            if (isinstance(cell, (Robot))
                    or (cell.pos in self.current_path_visited_dict) # Ya se visitó en el recorrido actual
                    or (isinstance(cell, Cell) and cell.is_apartada) # Ya está apartada la celda
                    or (self.is_lifting_box and isinstance(cell, Shelf) and cell.is_occupied)): # No se puede pasar por un estante ocupado mientras se carga una caja           
                blocked_positions.add(cell.pos)

        neighbor_positions = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        # Quitar todos los agentes de las posiciones bloqueadas
        allowed_positions = [pos for pos in neighbor_positions if pos not in blocked_positions]
        return allowed_positions

    def move_to_target_position(self):
        allowed_positions = self.get_valid_neighbors()

        if len(allowed_positions) == 0:
            self.dont_move()
            return
        
        neighbors_by_distance = self.order_neighbors_by_distance(allowed_positions, self.target_position)
        self.sig_pos = neighbors_by_distance[0]
        self.apartar_pos(self.sig_pos)


    def step(self):
        # print("objetivos: ", len(self.objectives_assigned))
        # print("objetivo actual: ", self.current_objective)
        # print("is charging: ", self.is_charging)
        # print("target position: ", self.target_position)

        if self.cur_charge == 0:
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
            self.dont_move()
            return
        
        if len(self.objectives_assigned) > 0:
            self.target_position = self.objectives_assigned[self.current_objective][0]

        self.move_to_target_position()


    # def move_to_charge_station(self, neighbors):

    #     if self.is_charging:
    #         self.cur_charge = min(self.cur_charge+self.charge_rate, self.max_charge)

    #         # Comprobar si ya está completamente cargado
    #         if self.cur_charge >= self.max_charge:
    #             self.is_charging = False
    #             self.num_recharges += 1
    #             print("sumó recargas")
    #             print(self.num_recharges)
    #             self.move_to_new_pos(neighbors)
    #             # self.target_position = None  # No hay objetivo actual
    #         else:
    #             self.dont_move()

    #         return
        
    #     estacion_carga_mas_cercana = self.find_closest_tile(is_target=lambda celda: isinstance(celda, Cell) and celda.es_estacion_carga, is_valid=lambda celda: isinstance(celda, Cell))

    #     if estacion_carga_mas_cercana.pos == self.pos:
    #         self.is_charging = True
    #         self.dont_move()
    #     else:
    #         self.target_position = estacion_carga_mas_cercana
    #         self.move_to_target_cell(neighbors)
    #         #self.sig_pos = estacion_carga_mas_cercana.pos
    #         self.necesita_carga = True  # Necesita llegar a la estación de carga
   

    def get_action(self) -> AgentAction:
        self.cur_action_type = None

        if self.cur_action_type == None:
            self.cur_action_type = ActionType.MOVE

        return AgentAction(_from=GridPosition(self.pos[0], self.pos[1]), _to=GridPosition(self.sig_pos[0], self.sig_pos[1]), _type=self.cur_action_type)

    def advance(self):
        self.cur_agent_action = self.get_action()
        
        if self.pos != self.sig_pos:
            self.free_pos(self.pos)
            self.movements += 1  
            self.cur_charge -= 1  
        else :
            self.cur_charge -= 1

        self.model.grid.move_agent(self, self.sig_pos)
