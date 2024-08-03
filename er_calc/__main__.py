import argparse
import datetime as dt
import json

from er_calc.asset import Asset
from er_calc.config import SimulationConfig
from er_calc.simulation import Simulation
from er_calc.strategy import SaveEarningsMinusExpenses, InvestFractionOfCashAfterBuffer
from er_calc.metric import TotalAssets, HoldingsByAsset, FIReached


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start_year", type=float, default=dt.date.today().year, required=False)
    ap.add_argument("--end_year", type=float, default=dt.date.today().year + 12, required=False)
    return ap.parse_args()


def simulate(args: argparse.Namespace) -> None:
    metrics = [
        FIReached(0.03),
        HoldingsByAsset(),
        TotalAssets(),
    ]
    Simulation(
        metrics=metrics,
        strategies=[
            SaveEarningsMinusExpenses(),
            InvestFractionOfCashAfterBuffer(
                buffer_per_yearly_expenses=0.5,
                allocation={
                    Asset.SAVINGS_ACCOUNT_VARIABLE_RATE: 0.2,
                    Asset.ETF_GLOBAL_STOCK: 0.8,
                    # Asset.CASH: 1.0,
                },
            ),
        ],
        config=SimulationConfig.from_namespace(args),
    ).run()
    captured_metrics = {}
    for metric in metrics:
        captured_metrics[metric.name()] = metric.values
    return captured_metrics


def main() -> None:
    args = parse_args()

    start_time = dt.datetime.now(dt.UTC)
    captured_metrics = simulate(args)
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
