from django.db import transaction
from django.core.exceptions import ValidationError
from attendance.models.leave_models import LeaveDecisionModel, LeaveModel,EmployeeModel
from django.db import transaction
from django.core.exceptions import ValidationError
from attendance.models.leave_models import LeaveDecisionModel, LeaveModel
from attendance.models import EmployeeModel




@transaction.atomic
def process_leave_decision(decision_id, approve: bool, actor: EmployeeModel) -> None:
    """
    Handle approval/rejection of a leave decision.
    - Only the matching role can act on its decision.
    - Dept Head can only approve leaves of their own department.
    - Any rejection finalizes the leave as REJECTED.
    - Director approval finalizes the leave as APPROVED and skips remaining steps.
    - If all roles approve, leave becomes APPROVED.
    """

    # ✅ Lock only the decision row itself (safe, no outer join issues)
    decision = LeaveDecisionModel.objects.select_for_update().get(pk=decision_id)

    # ✅ Eager-load related objects without locking
    decision = LeaveDecisionModel.objects.select_related(
        "approval_level", "application", "application__emp"
    ).get(pk=decision.id)

    leave = decision.application

    # --- Validations ---
    if leave.application_status != LeaveModel.ApplicationStatusChoices.pending:
        raise ValidationError("Leave already finalized.")

    if decision.status != LeaveDecisionModel.DecisionType.pending:
        raise ValidationError("This decision is already taken.")

    if actor.role != decision.approval_level.role:
        raise ValidationError("You are not authorized to act on this decision.")

    if actor.role == EmployeeModel.RoleType.dept_head:
        if actor.department != leave.emp.department:
            raise ValidationError("You can only approve leaves of your own department employees.")

    # --- Update decision ---
    decision.status = (
        LeaveDecisionModel.DecisionType.approved if approve
        else LeaveDecisionModel.DecisionType.declined
    )
    decision.decided_by = actor
    # decision.remarks = remarks or ""
    decision.save()

    # --- If rejected → finalize as REJECTED ---
    if not approve:
        leave.application_status = LeaveModel.ApplicationStatusChoices.rejected
        leave.save(update_fields=["application_status"])
        emp = leave.emp
        num_days = (leave.leave_to - leave.leave_from).days + 1
        if leave.leave_type != LeaveModel.LeaveTypeChoices.lwp:
            field_map = {
                LeaveModel.LeaveTypeChoices.sl: "sl",
                LeaveModel.LeaveTypeChoices.cl: "cl",
                LeaveModel.LeaveTypeChoices.pl: "pl",
                LeaveModel.LeaveTypeChoices.oh: "optional_holidays",
                LeaveModel.LeaveTypeChoices.comp_off: "comp_off",
            }
            field = field_map.get(leave.leave_type)
            if field:
                current = getattr(emp, field, 0)
                setattr(emp, field, current + num_days)
                emp.save(update_fields=[field])
        
        return

    # --- If Director approves → finalize as APPROVED immediately ---
    if actor.role == EmployeeModel.RoleType.director:
        leave.application_status = LeaveModel.ApplicationStatusChoices.approved
        leave.save(update_fields=["application_status"])

        # Skip all other pending decisions
        # LeaveDecisionModel.objects.filter(
        #     application=leave,
        #     status=LeaveDecisionModel.DecisionType.pending
        # ).exclude(id=decision.id).update(
        #     status=LeaveDecisionModel.DecisionType.declined,
        #     remarks="Skipped due to Director approval"
        # )
        # return

    # --- If no pending decisions remain → finalize as APPROVED ---
    if not LeaveDecisionModel.objects.filter(
        application=leave,
        status=LeaveDecisionModel.DecisionType.pending
    ).exists():
        leave.application_status = LeaveModel.ApplicationStatusChoices.approved
        leave.save(update_fields=["application_status"])


# @transaction.atomic
# def process_leave_decision(decision_id, approve: bool,  actor) -> None:
#     decision = LeaveDecisionModel.objects.select_for_update().select_related(
#         "approval_level", "application"
#     ).get(pk=decision_id)
#     leave = decision.application

#     if leave.application_status != LeaveModel.ApplicationStatusChoices.pending:
#         raise ValidationError("Leave already finalized.")

#     if decision.status != LeaveDecisionModel.DecisionType.pending:
#         raise ValidationError("This decision is already taken.")

#     # strict role check
#     if actor.role != decision.approval_level.role:
#         raise ValidationError("You are not authorized to act on this decision.")
    
#     if actor.role == EmployeeModel.RoleType.dept_head:
#         if actor.department != leave.emp.department:
#             raise ValidationError("You can only approve leaves of your own department employees.")


#     # update this decision
#     decision.status = LeaveDecisionModel.DecisionType.approved if approve else LeaveDecisionModel.DecisionType.declined
#     decision.decided_by = actor
#     # decision.remarks = remarks or ""
#     decision.save()

#     # rejection → finalize
#     if not approve:
#         leave.application_status = LeaveModel.ApplicationStatusChoices.rejected
#         leave.save(update_fields=["application_status"])
#         return

#     # director approval → finalize
#     if actor.role == "DIRECTOR":
#         leave.application_status = LeaveModel.ApplicationStatusChoices.approved
#         leave.save(update_fields=["application_status"])
#         # LeaveDecisionModel.objects.filter(
#         #     application=leave,
#         #     status=LeaveDecisionModel.DecisionType.pending
#         # ).exclude(id=decision.id).update(
#         #     status=LeaveDecisionModel.DecisionType.declined,
#         #     # remarks="Skipped due to Director approval"
#         # )
#         return

#     # check if all approved
#     if not LeaveDecisionModel.objects.filter(
#         application=leave, status=LeaveDecisionModel.DecisionType.pending
#     ).exists():
#         leave.application_status = LeaveModel.ApplicationStatusChoices.approved
#         leave.save(update_fields=["application_status"])
