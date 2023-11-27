import random

import mesa

from agent_models.Cell import Cell
from agent_models.Box import Box
from agent_models.Robot import Robot
from agent_models.Room import Room
from agent_models.ChargingStation import ChargingStation
from agent_models.Shelf import Shelf
from agent_models.ShippingShelf import ShippingShelf
from agent_models.ConveyorBelt import ConveyorBelt

MAX_NUMBER_ROBOTS = 20
MAX_NUMBER_IN_BOXES_PER_MINUTE = 60
MAX_NUMBER_OUT_BOXES_PER_MINUTE = 60

MIN_CHARGE = 70

def agent_portrayal(agent):
    if isinstance(agent, Robot):
        portrayal = {"Shape": "circle", "Filled": "false", "Color": "black", "Layer": 1, "r": 1.0,
                "text": f"{agent.cur_charge}", "text_color": "white"}
        if agent.cur_charge <= 0:
            portrayal["Color"] = "red"
        elif agent.cur_charge <= MIN_CHARGE:
            portrayal["Color"] = "orange"
        elif agent.is_lifting_box:
            portrayal["Color"] = "blue"
        
        return portrayal
    
    elif isinstance(agent, Box):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 2, "Color": "white",
                "w": 0.5, "h": 0.5, "text_color": "Black", "text": "📦"}
        if agent.is_apartada:
            portrayal["Color"] = "red"
        return portrayal
    
    elif isinstance(agent, ConveyorBelt):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 1, "w": 0.9, "h": 0.9, 
                     "Color": "white", "text_color": "Black", "text": "🎞️"}

        return portrayal

    elif isinstance(agent, ShippingShelf):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 1, "w": 0.9, "h": 0.9, 
                     "Color": "white", "text_color": "Black", "text": "⬆️"}
        if agent.is_apartado:
            portrayal["Color"] = "red"
        return portrayal
        
    elif isinstance(agent, Cell):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0, "w": 0.9, "h": 0.9, "text_color": "Black"}
        portrayal["Color"] = "white"
        portrayal["text"] = ""
        if agent.is_apartada:
            portrayal["Color"] = "red"
        return portrayal
    
    elif isinstance(agent, ChargingStation):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 1, "w": 0.9, "h": 0.9, 
                     "Color": "black", "text_color": "Black", "text": "🔋"}
        if agent.is_apartada:
            portrayal["Color"] = "red"
        return portrayal
    
    elif isinstance(agent, Shelf):
        portrayal = {"Shape": "rect", "Filled": "true", "Layer": 1, "w": 0.9, "h": 0.9, 
                     "Color": "white", "text_color": "Black", "text": "🪑"}
        if agent.is_apartado:
            portrayal["Color"] = "red"
        elif agent.is_occupied:
            portrayal["Color"] = "blue"
        return portrayal


grid = mesa.visualization.CanvasGrid(
    agent_portrayal, 20, 20, 400, 400)

chart_pending_shipments = mesa.visualization.ChartModule(
    [{"Label": "OutBoxesNeeded", "Color": '#36A2EB', "label": "Peding Shipments"}],
    50, 200,
    data_collector_name="datacollector"
)

chart_shipped_orders = mesa.visualization.ChartModule(
    [{"Label": "OutBoxesShipped", "Color": '#36A2EB', "label": "Shipped Orders"}],
    50, 200,
    data_collector_name="datacollector"
)


model_params = {
    "num_robots": mesa.visualization.Slider(
        "Número de Robots",
        1,
        1,
        MAX_NUMBER_ROBOTS,
        1,
        description="Escoge cuántos robots deseas implementar en el modelo",
    ),
    "modo_pos_inicial": mesa.visualization.Choice(
        "Posición Inicial de los Robots",
        "Aleatoria",
        ["Fija", "Aleatoria"],
        "Selecciona la forma se posicionan los robots"
    ),
    "in_boxes_per_minute": mesa.visualization.Slider(
        "Número de cajas que entran por minuto",
        1,
        1,
        MAX_NUMBER_IN_BOXES_PER_MINUTE,
        1,
        description="Escoge cuántas cajas entran por minuto",
    ),
    "out_boxes_per_minute": mesa.visualization.Slider(
        "Número de cajas que salen por minuto",
        1,
        1,
        MAX_NUMBER_OUT_BOXES_PER_MINUTE,
        1,
        description="Escoge cuántas cajas salen por minuto",
    ),
    "M": 20,
    "N": 20,
}

visualization = mesa.visualization.ModularServer(
    Room, [grid, chart_pending_shipments, chart_shipped_orders],
    "Reto Grafiteros", model_params, 8523
)
