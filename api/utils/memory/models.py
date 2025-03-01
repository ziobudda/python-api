# api/utils/memory/models.py
from dataclasses import dataclass
from typing import Dict, Optional, Any, List
from datetime import datetime
from pydantic import BaseModel

@dataclass
class Interaction:
    id: str
    timestamp: datetime
    agent_id: str  # Identificatore dell'agent chiamante
    command: str
    prompt: str
    response: str
    cost: Optional[float] = None  # Costo dell'operazione (es. costo API)
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id,
            'command': self.command,
            'prompt': self.prompt,
            'response': self.response,
            'cost': self.cost,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Interaction':
        return cls(
            id=data['id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            agent_id=data['agent_id'],
            command=data['command'],
            prompt=data['prompt'],
            response=data['response'],
            cost=data.get('cost'),
            metadata=data.get('metadata', {})
        )

# Modelli Pydantic per API
class InteractionCreate(BaseModel):
    agent_id: str
    command: str
    prompt: str
    response: str
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class InteractionResponse(BaseModel):
    id: str
    timestamp: str
    agent_id: str
    command: str
    prompt: str
    response: str
    cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class InteractionsListResponse(BaseModel):
    interactions: List[InteractionResponse]
    count: int