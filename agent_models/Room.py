from mesa.model import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from mesa.datacollection import DataCollector

from collections import deque

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot

import numpy as np


class Room(Model):
    def __init__(self, M: int, N: int,
                 num_robots: int = 5,
                 modo_pos_inicial: str = 'Fija',
                 ):

        super().__init__()
        self.current_id = 0

        self.num_robots = num_robots

        self.grid = MultiGrid(M, N, False)
        self.schedule = SimultaneousActivation(self)

        available_positions = [pos for _, pos in self.grid.coord_iter()]

        # Posicionamiento de celdas
        for id, pos in enumerate(available_positions):
            cell = Cell(int(f"{num_robots}{id}") + 1, self)
            self.grid.place_agent(cell, pos)

        # Posicionamiento de la caja
        box_position = (N//2, M//2)
        box = Box(1234562341, self)
        self.grid.place_agent(box, box_position)
        available_positions.remove(box_position)

        # Posicionamiento de agentes robot
        if modo_pos_inicial == 'Aleatoria':
            start_pos_robots = self.random.sample(available_positions, k=num_robots)
        else:  # 'Fija'
            start_pos_robots = [(1, 1)] * num_robots

        for id in range(num_robots):
            robot = Robot(id, self)
            self.grid.place_agent(robot, start_pos_robots[id])
            self.schedule.add(robot)

        # self.datacollector = DataCollector(
        #     model_reporters={"Grid": get_grid, "Recargas": get_recargas,
        #                      "CeldasSucias": get_sucias, "Movimientos": get_movimientos},
        # )

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def step(self):
        # self.datacollector.collect(self)

        self.schedule.step()

# def get_grid(model: Model) -> np.ndarray:
#     """
#     Método para la obtención de la grid y representarla en un notebook
#     :param model: Modelo (entorno)
#     :return: grid
#     """
#     grid = np.zeros((model.grid.width, model.grid.height))
#     for cell in model.grid.coord_iter():
#         cell_content, pos = cell
#         x, y = pos
#         for obj in cell_content:
#             if isinstance(obj, Robot):
#                 grid[x][y] = 2
#             elif isinstance(obj, Cell):
#                 grid[x][y] = int(obj.sucia)
#     return grid


# def get_recargas(model: Model) -> int:
#     sum_recargas = 0
#     for cell in model.grid.coord_iter():
#         cell_content, pos = cell
#         for obj in cell_content:
#             if isinstance(obj, Robot):
#                 sum_recargas += obj.num_recargas

#     return sum_recargas

# def get_sucias(model: Model) -> int:
#     """
#     Método para determinar el número total de celdas sucias
#     :param model: Modelo Mesa
#     :return: número de celdas sucias
#     """
#     sum_sucias = 0
#     for cell in model.grid.coord_iter():
#         cell_content, pos = cell
#         for obj in cell_content:
#             if isinstance(obj, Cell) and obj.sucia:
#                 sum_sucias += 1
    
#     return sum_sucias / model.num_celdas_sucias

# def get_movimientos(model: Model) -> int:
#     sum_movimientos = 0
#     for cell in model.grid.coord_iter():
#         cell_content, pos = cell
#         for obj in cell_content:
#             if isinstance(obj, Robot):
#                 sum_movimientos += obj.movimientos

#     return sum_movimientos



