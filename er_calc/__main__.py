import argparse
import datetime as dt
import importlib.util
import json

from er_calc.config import SimulationConfig
from er_calc.simulation import Simulation


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--config",
        type=str,
        required=True,
        help=(
            "Path to a .py file defining a `get_config` function, taking no arguments, and returning "
            "a SimulationConfig."
        ),
    )
    return ap.parse_args()


def load_simulation_config(config_path: str) -> SimulationConfig:
    spec = importlib.util.spec_from_file_location("er_calc._dynamically_loaded.config", config_path)

    if spec is None:
        raise ValueError(f"Config path didn't point to a valid python file: {config_path}.")
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    try:
        config = module.get_config()
    except AttributeError:
        raise ValueError(f"Config file didn't define get_config function: {config_path}.")

    if not isinstance(config, SimulationConfig):
        raise ValueError(
            f"get_config did not return a SimulationConfig: {config_path}, {type(config)}."
        )

    return config


def simulate(config: SimulationConfig) -> None:
    Simulation(
        config=config,
    ).run()
    captured_metrics = {}
    for metric in config.metrics:
        captured_metrics[metric.name()] = metric.values
    return captured_metrics


def main() -> None:
    args = parse_args()

    config = load_simulation_config(args.config)

    start_time = dt.datetime.now(dt.UTC)
    captured_metrics = simulate(config)
    end_time = dt.datetime.now(dt.UTC)

    result_dict = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "args": vars(args),
        "metrics": captured_metrics,
    }

    print(json.dumps(result_dict))


if __name__ == "__main__":
    main()
