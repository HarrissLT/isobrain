from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Optional

@dataclass
class Entity:
    name: str
    value: Any

@dataclass
class IntentMatch:
    intent_name: str
    confidence: float
    entities: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable] = None