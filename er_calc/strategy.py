import math

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TypeVar

from er_calc.asset import Asset
from er_calc.portfolio import Portfolio, Expense, Income


@dataclass
class Strategy(ABC):
    @abstractmethod
    def requested_assets(self) -> list[Asset]:
        ...

    def update_expenses(self, expenses: dict[Expense, float], year: float, increment: float):
        pass

    def update_income(self, income: dict[Income, float], year: float, increment: float):
        pass

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        ...


StrategyType = TypeVar('StrategyType', bound=Strategy)


@dataclass
class LimitedDurationStrategy(Strategy):
    """Only execute the child strategy for times in the interval
    [start, end] (inclusive).
    """
    child: StrategyType
    start: float = -math.inf
    end: float = math.inf
    relative: bool = True

    elapsed: float = field(default=0.0, init=False)

    def requested_assets(self) -> set[Asset]:
        return self.child.requested_assets()

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        if self.relative:
            if not math.isnan(increment):
                self.elapsed += increment
            if self.start <= self.elapsed <= self.end:
                self.child.execute(portfolio, year, increment)
        else:
            if self.start <= year <= self.end:
                self.child.execute(portfolio, year, increment)


@dataclass
class FixedYearlyInvestmentStrategy(Strategy):
    asset: Asset
    amount: float

    def requested_assets(self) -> set[Asset]:
        return {self.asset}

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        portfolio.add(asset=self.asset, cash=self.amount * increment)


class EarnPostTaxIncome(Strategy):
    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH}

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        TRADING_ALLOWANCE = 1000
        PROPERTY_ALLOWANCE = 1000
        POST_ALLOWANCE_TAX_BANDS = [
            (0.2, 37_700),
            (0.4, 125_140),
            (0.45, math.inf),
        ]
        CLASS_1_NI_BANDS = [
            (0.08, 4189 * 12),
            (0.02, math.inf),
        ]
        CLASS_4_NI_BANDS = [
            (0.00, 12570),
            (0.06, 50270),
            (0.02, math.inf),
        ]

        rental = portfolio.income[Income.UK_RENTAL]
        trading = portfolio.income[Income.UK_TRADING]
        salary = portfolio.income[Income.UK_SALARY]

        taxable = (
            max(0, rental - PROPERTY_ALLOWANCE)
            + max(0, trading - TRADING_ALLOWANCE)
            + salary
        )

        personal_allowance = max(0, 1250 - max(taxable - 100000, 0) / 2)

        remaining_taxable = taxable - personal_allowance
        tax = 0

        for rate, upper_limit in POST_ALLOWANCE_TAX_BANDS:
            taxable_at_rate = min(upper_limit, remaining_taxable)
            tax += taxable_at_rate * rate
            remaining_taxable -= taxable_at_rate

        remaining_salary = salary
        national_insurance = 0

        for rate, upper_limit in CLASS_1_NI_BANDS:
            taxable_at_rate = min(upper_limit, remaining_salary)
            national_insurance += taxable_at_rate * rate
            remaining_salary -= taxable_at_rate

        remaining_trading = trading

        for rate, upper_limit in CLASS_4_NI_BANDS:
            taxable_at_rate = min(upper_limit, remaining_trading)
            national_insurance += taxable_at_rate * rate
            remaining_salary -= taxable_at_rate

        cash_gained = rental + trading + salary - tax - national_insurance - portfolio.total_expenses()
        portfolio.add(Asset.CASH, cash=cash_gained)


@dataclass
class CareerExponential(Strategy):
    starting_salary: float
    yearly_salary_growth: float

    start_year: float | None = field(default=None, init=False)

    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH}

    def __salary_at_time(self, t: float):
        return (1 + self.yearly_salary_growth) ** (t - self.start_year) * self.starting_salary

    def update_income(self, income: dict[Income, float], year: float, increment: float):
        if self.start_year is None:
            self.start_year = year
            salary_before = 0.0
        else:
            salary_before = self.__salary_at_time(year - increment)

        salary_now = self.__salary_at_time(year)

        income[Income.UK_SALARY] += salary_now - salary_before


@dataclass
class BusinessConstant(Strategy):
    yearly_profit: float

    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH}

    def update_income(self, income: dict[Income, float], year: float, increment: float):
        income[Income.UK_TRADING] = self.yearly_profit


@dataclass
class InvestFractionOfCashAfterBuffer(Strategy):
    buffer_per_yearly_expenses: float
    allocation: dict[Asset, float]

    def __post_init__(self):
        if abs(sum(self.allocation.values()) - 1.0) > 1e-12:
            raise ValueError("Allocation ratios must add up to one")
        if any([ratio < 0.0 for ratio in self.allocation.values()]):
            raise ValueError("Allocation ratios cannot be negative")

    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH} | set(self.allocation.keys())

    def execute(self, portfolio: Portfolio, year: float, increment: float) -> None:
        yearly_buffer = self.buffer_per_yearly_expenses * sum(portfolio.expenses.values())
        investable = (portfolio.cash_of_asset_held(Asset.CASH) - yearly_buffer) * increment
        if investable < 0:
            return

        for asset, ratio in self.allocation.items():
            portfolio.add(asset, cash=investable * ratio)

        portfolio.add(Asset.CASH, cash=-investable)


@dataclass
class SimpleSpendingWithCreep(Strategy):
    initial_spending: float
    creep_rate: float

    start_year: float | None = field(default=None, init=False)

    def __at_time_t(self, t: float):
        return self.initial_spending * (1 + self.creep_rate) ** (t - self.start_year)

    def requested_assets(self) -> set[Asset]:
        return {Asset.CASH}

    def update_expenses(self, expenses: dict[Expense, float], year: float, increment: float) -> None:
        if self.start_year is None:
            self.start_year = year
            expenses_pre = 0
        else:
            expenses_pre = self.__at_time_t(year - increment)
        expenses_now = self.__at_time_t(year)

        expenses[Expense.LIVING] += expenses_now - expenses_pre
