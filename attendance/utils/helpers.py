from django.utils import timezone
from attendance.models.attendance_model import AttendanceModel
from collections import defaultdict
import datetime, calendar



def get_month_range(year=None, month=None):
    """
    Return (start_of_month, end_of_month) for the given year and month.
    Defaults to the current month if year or month is not provided.
    """
    # Use current year and month if not provided
    if year is None:
        year = timezone.now().year
    if month is None:
        month = timezone.now().month
    # Validate the month
    if not (1 <= month <= 12):
        raise ValueError("Invalid month. Must be between 1 and 12.")
    # Calculate the first day of the month
    start_of_month = datetime.datetime(year, month, 1)
    # Calculate the last day of the month
    # Using calendar.monthrange(year, month) to get the number of days in the month
    _, last_day = calendar.monthrange(year, month)
    end_of_month = datetime.datetime(year, month, last_day, 23, 59, 59, 999999)
    return start_of_month, end_of_month


def group_punches_by_day(qs):
    """
    Given a queryset annotated with .day (TruncDate), ordered by day,timestamp,
    return a dict mapping day -> list of recs for that day.
    """
    punches_by_day = {}
    for rec in qs:
        punches_by_day.setdefault(rec.day, []).append(rec)
    return punches_by_day


def process_day_records(recs):
    """
    Given list of attendance records for one day (ordered by timestamp),
    apply the pairing logic, return:
        - day_total_duration: datetime.timedelta
        - first_matched_in: datetime or None
        - last_matched_out: datetime or None
    """
    in_time = None
    day_total = datetime.timedelta(0)
    first_matched_in = None
    last_matched_out = None
    for rec in recs:
        if rec.punched_status == AttendanceModel.PunchedType.punch_in:
            if in_time is None:
                in_time = rec.timestamp
            else:
                # previous IN was unmatched; drop it, start new IN
                in_time = rec.timestamp
        elif rec.punched_status == AttendanceModel.PunchedType.punch_out:
            if in_time is not None:
                duration = rec.timestamp - in_time
                if duration.total_seconds() > 0:
                    day_total += duration
                    if first_matched_in is None:
                        first_matched_in = in_time
                    last_matched_out = rec.timestamp
                # reset for next pair
                in_time = None
            else:
                # OUT without IN — ignore
                continue
    return day_total, first_matched_in, last_matched_out


def average_times(time_list):
    """
    Given a list of time objects, return average time (time object),
    or None if list is empty.
    """
    if not time_list:
        return None
    total_secs = 0
    for t in time_list:
        total_secs += t.hour * 3600 + t.minute * 60 + t.second
    avg_sec = total_secs / len(time_list)
    h = int(avg_sec // 3600)
    m = int((avg_sec % 3600) // 60)
    s = int(avg_sec % 60)
    return datetime.time(hour=h, minute=m, second=s)



def process_punchs(objs):
    grouped = defaultdict(list)
    for entry in objs:
        timestamp = entry.timestamp 
        punched_status = entry.punched_status
        punch_date = timestamp.date()
        punch_time = timestamp.time()
        grouped[str(punch_date)].append((punched_status,punch_time))
    return grouped
