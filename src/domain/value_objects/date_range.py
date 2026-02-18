"""DateRange value object."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DateRange:
    """
    Immutable value object representing a date range.
    
    Ensures start_date is always before or equal to end_date.
    """
    
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        """Validate date range."""
        if self.start_date > self.end_date:
            raise ValueError(
                f"start_date ({self.start_date}) must be before or equal to "
                f"end_date ({self.end_date})"
            )
    
    def contains(self, date: datetime) -> bool:
        """Check if a date falls within this range."""
        return self.start_date <= date <= self.end_date
    
    def days_count(self) -> int:
        """Calculate the number of days in this range."""
        return (self.end_date - self.start_date).days + 1
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.start_date.date()} to {self.end_date.date()}"
