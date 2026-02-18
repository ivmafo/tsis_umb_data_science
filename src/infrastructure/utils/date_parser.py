from datetime import datetime, time as datetime_time
from typing import Optional, Union

class DateParser:
    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime.date]:
        """Robust date parser."""
        date_str = str(date_str).replace(".0", "").strip()
        if not date_str or date_str.lower() in ['nan', 'none', 'nat', '']:
            return None

        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
            try:
                # Returns date object directly
                # If we were using polars map_elements with return_dtype=pl.Date, 
                # we should return a python date object.
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue

        try:
            length = len(date_str)
            if length == 6: return datetime.strptime(date_str, '%d%m%y').date()
            elif length == 5:
                # ddmmyy with d as single digit? or dmyyy?
                # Assuming d-mm-yy where d is 1 digit
                day, month, year = int(date_str[:1]), int(date_str[1:3]), int("20" + date_str[3:])
                return datetime(year, month, day).date()
            elif length == 4:
                # mmyy
                month, year = int(date_str[:2]), int("20" + date_str[2:])
                return datetime(year, month, 1).date()
            elif length == 3:
                # dmy where m is 1 digit? Very ambiguous.
                # Assuming d-m-y where d is 1 digit, m is 1 digit
                day, month, year = int(date_str[:1]), int(date_str[1:2]), int("20" + date_str[2:])
                return datetime(year, month, day).date()
        except:
             pass
        return None

    @staticmethod
    def parse_time(time_str: str) -> Optional[datetime_time]:
        """Robust time parser."""
        time_str = str(time_str).replace(".0", "").strip()
        if not time_str or time_str.lower() in ['nan', 'none', 'nat', '']:
            return None
        time_str = time_str.zfill(4)
        try:
            if '.' in time_str:
                 parts = time_str.split('.')
                 main = parts[0]
                 if len(main) > 4: return datetime_time(int(main[:2]), int(main[2:]))
                 elif len(main) < 2: return datetime_time(0, int(main))
                 return None
            return datetime_time(int(time_str[:2]), int(time_str[2:]))
        except:
            return None
