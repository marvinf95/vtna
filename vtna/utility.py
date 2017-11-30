import abc


class Describable(abc.ABC):
    @abc.abstractmethod
    def get_name(self) -> str:
        pass

    @abc.abstractmethod
    def get_description(self) -> str:
        pass
