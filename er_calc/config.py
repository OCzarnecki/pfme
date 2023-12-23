from __future__ import annotations

import datetime as dt

from dataclasses import dataclass

import argparse


@dataclass
class SimulationConfig:
    # Size of simulation step [years]
    increment: float = 1.0

    start_year: float = float(dt.date.today().year)
    end_year: float = float(dt.date.today().year) + 50

    @staticmethod
    def from_namespace(args: argparse.Namespace) -> SimulationConfig:
        return SimulationConfig(**args._get_kwargs())
