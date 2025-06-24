from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel, validator


class ActionsRequest(BaseModel):
    entity_ids: List[str]
    actions: List[str]
    start_time: str
    end_time: str

    @validator('start_time', 'end_time')
    def validate_time_format(cls, value):
        try:
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d %H',
                '%Y-%m-%d'
            ]
            for fmt in formats:
                try:
                    datetime.strptime(value, fmt)
                    return value
                except ValueError:
                    continue
            raise ValueError('time must be in format YYYY-MM-DD [HH[:MM[:SS]]]')
        except ValueError as e:
            raise ValueError(str(e))


class ActionSession(BaseModel):
    action: str
    action_start: str
    action_end: str
    duration_seconds: float

class EntityResponse(BaseModel):
    entity_id: str
    actions: Dict[str, List[ActionSession]]
    total_duration: Dict[str, float]
    average_duration: Dict[str, float]
    session_count: Dict[str, int]