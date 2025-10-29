from dataclasses import dataclass
from typing import TypeVar, Generic, Optional


T = TypeVar("T")

@dataclass
class Result(Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None

    @staticmethod   
    def ok(data: T):
        return Result(success=True, data=data)
    
    @staticmethod
    def fail(error: str):
        return Result(success=False, error=error)