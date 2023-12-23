from abc import ABC, abstractmethod
from typing import TypeVar

from er_calc.asset import Asset
from er_calc.portfolio import Portfolio


class RunMetric(ABC):
    @abstractmethod
    def requested_assets(self) -> list[Asset]:
        ...

    def calculate(self, portfolio: Portfolio):
        ...


RunMetricType = TypeVar('MetricType', bound=RunMetric)
