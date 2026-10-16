from abc import ABC, abstractmethod

class BaseCrud(ABC):
    @abstractmethod
    def insert(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
