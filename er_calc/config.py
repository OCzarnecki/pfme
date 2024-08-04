from __future__ import annotations

import datetime as dt

from dataclasses import dataclass, field

import argparse

from pfme.asset import Asset, AssetProvider, ConstantGeomIncreaseAsset
from pfme.metric import RunMetricType
from pfme.strategy import StrategyType


@dataclass
class SimulationConfig:
    # Size of simulation step [years]
    metrics: list[RunMetricType]
    strategies: list[StrategyType]

    increment: float = 1.0

    start_year: float = float(dt.date.today().year)
    end_year: float = float(dt.date.today().year) + 50

    asset_provider_mapping: dict[Asset, AssetProvider] = field(default_factory=lambda: {
        Asset.SAVINGS_ACCOUNT_VARIABLE_RATE: ConstantGeomIncreaseAsset(100.0, 0.04),
        Asset.ETF_GLOBAL_STOCK: ConstantGeomIncreaseAsset(100.0, 0.06),
        Asset.CASH: ConstantGeomIncreaseAsset(1.0, 0.0),  # f(t) = 1
    })


    @staticmethod
    def from_namespace(args: argparse.Namespace) -> SimulationConfig:
        return SimulationConfig(**vars(args))
