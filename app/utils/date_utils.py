"""
Date utilities for the hotel PMS.
"""

from datetime import date, timedelta
from typing import List, Generator


def get_date_range(start_date: date, end_date: date) -> Generator[date, None, None]:
    """
    Generate all dates in a range (inclusive of start, exclusive of end).
    This matches hotel booking convention where check-out day is not charged.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (exclusive, check-out date)
    
    Yields:
        Each date in the range
    """
    current = start_date
    while current < end_date:
        yield current
        current += timedelta(days=1)


def get_date_list(start_date: date, end_date: date) -> List[date]:
    """
    Get a list of all dates in a range.
    
    Args:
        start_date: Start date (inclusive)
        end_date: End date (exclusive)
    
    Returns:
        List of dates
    """
    return list(get_date_range(start_date, end_date))


def count_nights(check_in: date, check_out: date) -> int:
    """
    Calculate the number of nights for a booking.
    
    Args:
        check_in: Check-in date
        check_out: Check-out date
    
    Returns:
        Number of nights
    """
    return (check_out - check_in).days


def validate_date_range(check_in: date, check_out: date) -> None:
    """
    Validate that the date range is valid for booking.
    
    Args:
        check_in: Check-in date
        check_out: Check-out date
    
    Raises:
        ValueError: If dates are invalid
    """
    today = date.today()
    
    if check_in < today:
        raise ValueError("Check-in date cannot be in the past")
    
    if check_out <= check_in:
        raise ValueError("Check-out date must be after check-in date")


def get_future_dates(days_ahead: int) -> List[date]:
    """
    Get a list of dates starting from today.
    
    Args:
        days_ahead: Number of days to generate
    
    Returns:
        List of future dates
    """
    today = date.today()
    return [today + timedelta(days=i) for i in range(days_ahead)]
