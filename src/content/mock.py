from typing import Dict, Any
from .base import ContentGenerator

class MockGenerator(ContentGenerator):
    """
    A mock implementation that returns hardcoded data.
    Useful for testing without API costs.
    """
    
    def generate(self, topic: str) -> Dict[str, Any]:
        return {
            "title": f"[Mock] 5 Tips for {topic}",
            "content": f"This is a mock post about {topic}.\n\n1. Tip One\n2. Tip Two\n3. Tip Three\n\n#mock #test",
            "image_prompt": f"A beautiful illustration of {topic}, minimal style"
        }
