from ..GridPosition import GridPosition

def serialize_grid_position_to_json(grid_position: GridPosition) -> dict:
    return {
        "x": grid_position.x,
        "z": grid_position.z
    }