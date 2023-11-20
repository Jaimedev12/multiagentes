from ..ActionType import ActionType

def serialize_action_type_to_json(action_type: ActionType) -> str:
    return action_type.value if action_type and hasattr(action_type, 'value') else None
