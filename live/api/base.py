import abc
from typing import Dict, Optional
from fastapi import HTTPException


class BaseChannel(abc.ABC):
    @abc.abstractmethod
    async def get_play_url(self, video_id: str) -> Optional[str]:
        """
        Placeholder method to be implemented by subclasses.
        """
        pass
