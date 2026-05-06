from datetime import datetime, timedelta, date
from typing import List, Optional


class EbbinghausScheduler:
    REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]

    def calculate_next_review(self, last_review_date: date, review_count: int, mastery_level: float) -> date:
        if review_count >= len(self.REVIEW_INTERVALS):
            base_interval = 60
        else:
            base_interval = self.REVIEW_INTERVALS[review_count]

        if mastery_level >= 0.9:
            interval = int(base_interval * 1.5)
        elif mastery_level >= 0.7:
            interval = base_interval
        elif mastery_level >= 0.5:
            interval = int(base_interval * 0.7)
        else:
            interval = int(base_interval * 0.5)

        interval = max(1, interval)
        return last_review_date + timedelta(days=interval)

    def get_review_urgency(self, next_review_date: date, today: date, mastery_level: float) -> str:
        days_diff = (next_review_date - today).days

        if days_diff < 0:
            return "overdue"
        elif days_diff == 0:
            return "due_today"
        elif days_diff <= 1:
            return "due_tomorrow"
        elif days_diff <= 3:
            return "due_soon"
        else:
            return "on_track"


scheduler = EbbinghausScheduler()
