from dataclasses import dataclass
from .GridPosition import GridPosition
from .ActionType import ActionType

@dataclass
class AgentAction:
    _from: GridPosition
    _to: GridPosition
    _type: ActionType
