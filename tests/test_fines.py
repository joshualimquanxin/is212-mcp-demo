import pytest

from libfines.fines import DAILY_RATE, late_fee


def test_rates_table_has_the_three_policy_item_types():
    assert set(DAILY_RATE) == {"book", "dvd", "magazine"}


def test_book_ten_days_late():
    assert late_fee("book", 10) == 5.00


def test_dvd_three_days_late():
    assert late_fee("dvd", 3) == 3.00


def test_magazine_four_days_late():
    assert late_fee("magazine", 4) == 1.00


def test_returned_on_time_is_free():
    assert late_fee("book", 0) == 0.00


def test_unknown_item_type_rejected():
    with pytest.raises(ValueError):
        late_fee("telescope", 1)


def test_negative_days_rejected():
    with pytest.raises(ValueError):
        late_fee("book", -1)
