from abc import ABC, abstractmethod

class BaseChecker(ABC):
    def __init__(self, card_data):
        self.card_data = card_data

    @abstractmethod
    def check(self):
        pass
