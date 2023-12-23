import argparse

from er_calc.config import SimulationConfig
from er_calc.simulation import Simulation


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    return ap.parse_args()


def simulate(args: argparse.Namespace) -> None:
    Simulation(
        metrics=[],
        strategies=[],
        config=SimulationConfig.from_namespace(args),
    ).run()


def main() -> None:
    args = parse_args()
    simulate(args)


if __name__ == "__main__":
    main()
