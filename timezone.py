import pytz
from datetime import datetime, timedelta

class timezone:
    @staticmethod
    def is_dst(targetdate, timezone="Europe/London"):
        # Convert string to datetime if needed
        if isinstance(targetdate, str):
            targetdate = datetime.strptime(targetdate, "%Y-%m-%d")

        tz = pytz.timezone(timezone)
        target = tz.localize(targetdate, is_dst=None)  # Make it timezone-aware

        # Check if DST is in effect for the target date
        if target.dst() != timedelta(0):  
            mambudate = str(target.date()) + "T01:00:00+01:00"
        else:
            mambudate = str(target.date()) + "T00:00:00Z"
        
        return mambudate