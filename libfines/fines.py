"""Late-fee calculation.

Daily rates follow the Library Fee Policy, section 2.
"""

# Dollars per day overdue, by item type.
DAILY_RATE = {
    "book": 0.50,
    "dvd": 1.00,
    "magazine": 0.25,
}


def late_fee(item_type: str, days_late: int) -> float:
    """Return the late fee in dollars for one item, rounded to 2 dp.

    Raises ValueError for an unknown item type or a negative number of days.
    """
    if item_type not in DAILY_RATE:
        raise ValueError(f"unknown item type: {item_type!r}")
    if days_late < 0:
        raise ValueError("days_late cannot be negative")
    return round(DAILY_RATE[item_type] * days_late, 2)
