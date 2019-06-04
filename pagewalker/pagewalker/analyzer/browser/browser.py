from abc import ABCMeta, abstractmethod


class Browser(metaclass=ABCMeta):
    @abstractmethod
    def run(self):
        pass
