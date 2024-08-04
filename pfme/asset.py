import math

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TypeVar


class Asset(Enum):
    CASH = auto(),
    ETF_GLOBAL_STOCK = auto(),
    SAVINGS_ACCOUNT_VARIABLE_RATE = auto(),


class AssetProvider(ABC):
    @abstractmethod
    def update_value(self, year: float, increment: float) -> None:
        """Update the asset value.

        Before this call, asset.value() is the value at time=year-increment.
        After this call, asset value() is the value at time=year.

        If isnan(increment) then the asset should set its initial value.
        """
        ...

    def value(self) -> float:
        ...


AssetProviderType = TypeVar('AssetProviderType', bound=AssetProvider)


class ConstantGeomIncreaseAsset(AssetProvider):
    # A value of 0.05 indicates 5% growth each year
    starting_value: float
    growth_rate: float

    _value: float

    def __init__(self, starting_value: float, growth_rate: float):
        self.starting_value = starting_value
        self.growth_rate = growth_rate
        self._value = starting_value

    def update_value(self, _year: float, increment: float) -> None:
        if not math.isnan(increment):
            self._value *= (1 + self.growth_rate) ** increment

    def value(self) -> float:
        return self._value
