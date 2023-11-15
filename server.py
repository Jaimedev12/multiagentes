import random

import mesa

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.Room import Room

MAX_NUMBER_ROBOTS = 20

def agent_portrayal(agent):
    if isinstance(agent, Robot):
        return {"Shape": "circle", "Filled": "false", "Color": "black", "Layer": 1, "r": 1.0,
                "text": f"{agent.cur_charge}", "text_color": "yellow"}
    # elif isinstance(agent, Mueble):
    #     return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 0,
    #             "w": 0.9, "h": 0.9, "text_color": "Black", "text": "🪑"}
    elif isinstance(agent, Box):
        return {"Shape": "rect", "Filled": "true", "Color": "white", "Layer": 2,
                "w": 0.9, "h": 0.9, "text_color": "Black", "text": "📦"}
    elif isinstance(agent, Cell):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        portrayal["Color"] = "white"
        portrayal["text"] = ""
        # if agent.sucia:
        #     portrayal["Color"] = "white"
        #     portrayal["text"] = "🦠"
        # elif agent.is_apartada:
        #     portrayal["Color"] = "red"
        # elif agent.es_estacion_carga:  
        #     portrayal["Color"] = "black"
        #     portrayal["text"] = "🔋"
        # else:
        #     portrayal["Color"] = "white"
        #     portrayal["text"] = ""
        return portrayal


grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 20, 20, 400, 400)

# chart_celdas = mesa.visualization.ChartModule(
#     [{"Label": "CeldasSucias", "Color": '#36A2EB', "label": "Celdas Sucias"}],
#     50, 200,
#     data_collector_name="datacollector"
# )

# chart_movimientos = mesa.visualization.ChartModule(
#     [{"Label": "Movimientos", "Color": '#36A2EB', "label": "Total de Movimientos"}],
#     50, 200, 
#     data_collector_name="datacollector"
# )

# chart_recargas = mesa.visualization.ChartModule(
#     [{"Label": "Recargas", "Color": '#36A2EB', "label": "Total de Recargas"}],
#     50, 200, 
#     data_collector_name="datacollector"
# )


model_params = {
    "num_robots": mesa.visualization.Slider(
        "Número de Robots",
        5,
        1,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    # "porc_celdas_sucias": mesa.visualization.Slider(
    #     "Porcentaje de Celdas Sucias",
    #     0.3,
    #     0.0,
    #     0.75,
    #     0.05,
    #     description="Selecciona el porcentaje de celdas sucias",
    # ),
    # "porc_muebles": mesa.visualization.Slider(
    #     "Porcentaje de Muebles",
    #     0.1,
    #     0.0,
    #     0.20,
    #     0.01,
    #     description="Selecciona el porcentaje de muebles",
    # ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Selecciona la forma se posicionan los robots"
    ),
    "M": 20,
    "N": 20,
}

server = mesa.visualization.ModularServer(
    Room, [grid],
    "Reto Grafiteros", model_params, 8521
)
