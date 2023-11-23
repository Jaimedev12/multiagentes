from mesa.agent import Agent
from collections import deque

from agent_models.Cell import Cell
from agent_models.Box import Box

from response_format.ActionType import ActionType
from response_format.AgentAction import AgentAction
from response_format.GridPosition import GridPosition

class Robot(Agent):

    max_charge = 100
    charge_rate = 25
    charge_limit = 40

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.sig_pos = None
        self.cur_charge = self.max_charge

        self.target_position = None
        self.objectives_assigned = list()
        self.current_objective = 0

        self.current_path_visited_dict = dict()
        self.is_charging = False
        self.cur_action_type = None
        self.cur_agent_action = None
        self.has_target_cell = False

        # Estadísticas
        self.movements = 0
        self.num_recharges = 0

    # def calc_dist(self, p1, p2):
    #     return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def dont_move(self):
        self.sig_pos = self.pos

    # def find_closest_tile(self, is_target, is_valid):
    #     queue = deque()
    #     queue.append(self.pos)
    #     visited = dict()

    #     while queue:
    #         cur_pos = queue.popleft()

    #         if cur_pos in visited:
    #             continue

    #         visited[cur_pos] = True
    #         neighbours = self.model.grid.get_neighbors(
    #             cur_pos, moore=True, include_center=False)
        
    #         for agent in neighbours:
    #             if is_target(agent):
    #                 return agent

    #             if is_valid(agent):
    #                 queue.append(agent.pos)

    #     return 0

    def get_neighbours_by_distance(self, neighbours, posicion_destino):
        distances = []
        for pos in neighbours:
            pos_with_distance = (self.calc_dist(pos, posicion_destino), pos)
            distances.append(pos_with_distance)

        distances.sort(key=lambda x: x[0])

        for i in range(len(neighbours)):
            neighbours[i] = distances[i][1]

        return neighbours
    
    # def move_to_new_pos(self, neighbours):
    #     if len(neighbours) == 0:
    #         self.dont_move()
    #         return
        
    #     if not isinstance(self.target_position, Cell):
    #         self.target_position = self.find_closest_tile(is_target=lambda agent: isinstance(agent, Box), is_valid=lambda agent: isinstance(agent, Cell))

    #     self.move_to_target_cell(neighbours)

    # def move_to_target_cell(self, neighbours):
    #     if self.target_position == 0:
    #         self.dont_move()
    #         return

    #     neighbours_with_priority = self.get_neighbours_by_distance(neighbours, self.target_position.pos)
    #     if len(neighbours_with_priority) > 0:
    #         self.sig_pos = neighbours_with_priority[0].pos
    #     else:
    #         self.dont_move()

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

    def charge(self):
        self.cur_charge = min(self.cur_charge+self.charge_rate, self.max_charge)

        if self.cur_charge == self.max_charge:
            self.is_charging = False
            self.num_recharges += 1

    def get_valid_neighbours(self):
        neighbour_agents = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False)
        
        # Marcar posiciones bloqueadas
        blocked_positions = set()
        for cell in neighbour_agents:
            if (isinstance(cell, (Robot))
               or (cell.pos in self.current_path_visited_dict) # Ya se visitó en el recorrido actual
               or (isinstance(cell, Cell) and cell.is_apartada)): # Ya está apartada la celda                
                blocked_positions.add(cell.pos)

        neighbour_positions = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False)

        # Quitar todos los agentes de las posiciones bloqueadas
        allowed_positions = [pos for pos in neighbour_positions if pos not in blocked_positions]
        return allowed_positions

    def move_to_target_position(self):
        allowed_positions = self.get_valid_neighbours()

        if len(allowed_positions) == 0:
            self.dont_move()
            return
        
        neighbours_by_distance = self.get_neighbours_by_distance(allowed_positions, self.target_position)
        self.sig_pos = neighbours_by_distance[0]
        self.apartar_pos(self.sig_pos)


    def step(self):
        if self.cur_charge == 0:
            self.dont_move()
            return
        
        if self.is_charging and self.cur_charge < self.charge_limit:
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
            self.objectives_assigned[self.current_objective][1]()

            self.current_objective += 1
            self.dont_move()
            return
        
        if self.target_position == None and len(self.objectives_assigned) > 0:
            self.target_position = self.objectives_assigned[self.current_objective][0]

        self.move_to_target_position()


    # def move_to_charge_station(self, neighbours):

    #     if self.is_charging:
    #         self.cur_charge = min(self.cur_charge+self.charge_rate, self.max_charge)

    #         # Comprobar si ya está completamente cargado
    #         if self.cur_charge >= self.max_charge:
    #             self.is_charging = False
    #             self.num_recharges += 1
    #             print("sumó recargas")
    #             print(self.num_recharges)
    #             self.move_to_new_pos(neighbours)
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
    #         self.move_to_target_cell(neighbours)
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
            # self.cur_charge = max(self.cur_charge, 0)

        self.model.grid.move_agent(self, self.sig_pos)
