from collections import defaultdict
from django.db import transaction
from attendance.models.attendance_model import AttendanceModel
from employee.models import EmployeeModel


def process_bulk_punches(entries, device=None):
    try:
        grouped = defaultdict(lambda: defaultdict(list))
        
        for entry in entries:
            emp_id = entry['emp_id']
            timestamp = entry['time']
            punch_date = timestamp.date()
            grouped[emp_id][punch_date].append(timestamp)
        new_records = []
        print(grouped)
        with transaction.atomic():
            for emp_id, date_group in grouped.items():
                employee = EmployeeModel.objects.get(exotic_id=emp_id)

                for punch_date, punches in date_group.items():
                    punches.sort()
                    print(punches)
                    last_record = (
                        AttendanceModel.objects
                        .filter(employee=employee, timestamp__date=punch_date)
                        .order_by('timestamp')
                        .last()
                    )
                    last_status = last_record.punched_status if last_record else None
                    for ts in punches:
                        if last_status == AttendanceModel.PunchedType.punch_in:
                            next_status = AttendanceModel.PunchedType.punch_out
                        else:
                            next_status = AttendanceModel.PunchedType.punch_in
                        new_records.append(
                            AttendanceModel(
                                employee=employee,
                                punched_status=next_status,
                                type=AttendanceModel.TypeChoices.hardware,
                                timestamp=ts,
                                device=device
                            )
                        )
                        last_status = next_status 
            AttendanceModel.objects.bulk_create(new_records)
        return new_records
    except Exception as e:
        print("ERROR: ", e)
        raise e