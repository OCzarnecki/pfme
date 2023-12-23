import math

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TypeVar


class Asset(Enum):
    ETF_GLOBAL_STOCK = auto(),
    SAVINGS_ACCOUNT_VARIABLE_RATE = auto(),


class AssetProvider(ABC):
    @abstractmethod
    def asset(self) -> Asset:
        ...

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
    growth_rate: float

    _asset: Asset
    _value: float

    def __init__(self, asset: Asset, growth_rate: float):
        self._asset = asset
        self.growth_rate = growth_rate
        self._value = 100.0

    def update_value(self, _year: float, increment: float) -> None:
        if not math.isnan(increment):
            self._value *= (1 + self.growth_rate) ** increment

    def value(self) -> float:
        return self._value

    def asset(self) -> Asset:
        return self._asset
