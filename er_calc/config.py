from __future__ import annotations

import datetime as dt

from dataclasses import dataclass, field

import argparse

from er_calc.asset import Asset, AssetProvider, ConstantGeomIncreaseAsset


@dataclass
class SimulationConfig:
    # Size of simulation step [years]
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
