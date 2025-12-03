from abc import ABC, abstractmethod
from typing import Dict, Any

class ContentGenerator(ABC):
    """
    Abstract base class for content generation strategies.
    Java Equivalent: public interface ContentGenerator
    """
    
    @abstractmethod
    def generate(self, topic: str) -> Dict[str, Any]:
        """
        Generates content based on a topic.
        
        Args:
            topic: The subject of the content.
            
        Returns:
            A dictionary containing:
            - title: str
            - content: str
            - image_prompt: str (optional)
        """
        pass
