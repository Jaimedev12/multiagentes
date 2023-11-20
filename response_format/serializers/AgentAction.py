from ..AgentAction import AgentAction

from .ActionType import serialize_action_type_to_json
from .GridPosition import serialize_grid_position_to_json

def serialize_agent_action_to_json(agent_action: AgentAction) -> dict:
    return {
        "from": serialize_grid_position_to_json(agent_action._from),
        "to": serialize_grid_position_to_json(agent_action._to),
        "type": serialize_action_type_to_json(agent_action._type)
    }