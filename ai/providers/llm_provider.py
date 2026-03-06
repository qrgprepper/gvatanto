from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def analyze(self, text):
        pass

    @abstractmethod
    def synthesize(self, summaries):
        pass