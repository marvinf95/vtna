import abc


class Describable(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass
