"""Domain rules, decimal quantities and conservative maintenance reminders."""
from __future__ import annotations
import calendar
from datetime import date
from decimal import Decimal, InvalidOperation

CATEGORIES = ['Preventive maintenance', 'General maintenance', 'Repair', 'Alteration', 'Annual inspection', '100-hour inspection', 'Progressive inspection', 'Other inspection', 'AD compliance', 'Component installation/removal', 'Inspection/test documentation', 'Historical entry', 'Other']
ROLES = ['Recordkeeping only', 'Pilot', 'Mechanic', 'Mechanic with IA', 'Repair station', 'Repairman', 'Other authorized person']
STATES = ['Draft', 'Ready to print', 'Printed / awaiting physical signature', 'Signed copy recorded', 'Historical import requiring verification']
DISCLAIMER = 'Recordkeeping only. No FAA approval, certificate verification or airworthiness determination. You are responsible for applicability, qualifications, actual work, accurate records and proper return-to-service approval. Generated documents require an appropriate physical signature.'

def quantity(value: object, label: str = 'Quantity') -> Decimal | None:
    if value is None or str(value).strip() == '':
        return None
    try:
        result = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(f'{label} must be a decimal number.') from None
    if not result.is_finite() or result < 0:
        raise ValueError(f'{label} must be finite and nonnegative.')
    return result

def iso_date(value: str, label: str = 'Date') -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(f'{label} must use YYYY-MM-DD.') from None

def calendar_due(completed: date, months: int, end_of_month: bool = True) -> date:
    if months < 1:
        raise ValueError('Calendar interval must be positive.')
    index = completed.year * 12 + completed.month - 1 + months
    year, month = divmod(index, 12)
    last = calendar.monthrange(year, month + 1)[1]
    return date(year, month + 1, last if end_of_month else min(completed.day, last))

def schedule_status(data: dict, times: dict, today: date | None = None) -> tuple[str, str]:
    today = today or date.today()
    if data.get('applicability') == 'Not applicable':
        return 'Not configured', 'Marked not applicable; verify rationale.'
    if data.get('applicability') != 'Applicable':
        return 'Unknown', 'Applicability needs review.'
    specialized=data.get('schedule_type','Custom')!='Custom'
    if specialized and (not data.get('applicability_confirmed') or not data.get('source_reference') or not data.get('baseline_reference')):
        return 'Unknown','Document applicability, controlling source and qualifying baseline before calculating.'
    if data.get('exception_basis') and not data.get('exception_reviewed'):
        return 'Unknown','The inspection-program/operating exception needs review.'
    if data.get('schedule_type')=='ELT battery':
        return elt_status(data,today)
    if specialized and data.get('interval_hours') and data.get('time_source')!='total_time' and not data.get('time_basis'):
        return 'Unknown','A regulatory hour reminder requires documented time-in-service basis; meters are not interchangeable.'
    if data.get('schedule_type')=='100-hour' and data.get('excess_hours'):
        excess=quantity(data['excess_hours'])
        if excess>10:return 'Unknown','Excess exceeds the limited en-route provision; independently review.'
        data=dict(data,interval_hours=str(Decimal('100')-excess))
    if data.get('completed'):
        return 'Completed', 'One-time tracking item completed.'
    checks, missing, detail = [], False, []
    due = iso_date(data.get('due_date', ''))
    if data.get('months'):
        last = iso_date(data.get('last_date', ''))
        if last:
            due = calendar_due(last, int(data['months']), data.get('calendar_month', True))
        else:
            missing = True
    if due:
        days = (due - today).days
        checks.append(3 if days < 0 else 2 if days == 0 else 1 if days <= int(data.get('lead_days') or 30) else 0)
        detail.append(f'Date: {due.isoformat()}')
    for suffix, current in [('hours', times.get(data.get('time_source', 'total_time'))), ('cycles', times.get('cycles'))]:
        interval = quantity(data.get('interval_' + suffix))
        threshold = quantity(data.get('due_' + suffix))
        if interval is not None:
            last = quantity(data.get('last_' + suffix))
            if last is None:
                missing = True
            else:
                threshold = last + interval
        if threshold is not None:
            detail.append(f'{suffix}: {threshold} ({data.get("time_source", "total_time") if suffix == "hours" else "cycles"})')
            value = quantity(current)
            if value is None:
                missing = True
            else:
                left = threshold - value
                lead = quantity(data.get('lead_' + suffix) or ('10' if suffix == 'hours' else '0'))
                checks.append(3 if left < 0 else 2 if left == 0 else 1 if left <= lead else 0)
    severity = max(checks, default=0)
    status = ['Upcoming', 'Upcoming', 'Due', 'Past recorded due threshold'][severity]
    if missing and severity < 2:
        status = 'Unknown'
    if not checks and not missing:
        status = 'Not configured'
    return status, '; '.join(detail) + ('; Missing required baseline/current value' if missing else '')

def validate_entry(data: dict) -> list[str]:
    errors = []
    historical = data.get('category') == 'Historical entry'
    fields = ['description', 'source_document'] if historical else ['date', 'description', 'performer']
    for key in fields:
        if not str(data.get(key, '')).strip():
            errors.append(key.replace('_', ' ').capitalize() + ' is required.')
    if data.get('date'):
        iso_date(data['date'])
    quantity(data.get('total_time'), 'Total time')
    if historical:
        return errors
    if not data.get('affirmed'):
        errors.append('Affirm responsibility for accuracy, work and applicable authorization.')
    inspection = 'inspection' in data.get('category', '').lower() and data.get('category') != 'Inspection/test documentation'
    disposition = data.get('disposition', 'Work documented only')
    if inspection:
        from .statements import review_errors
        errors.extend(review_errors(data))
        for key in ['extent', 'total_time', 'statement']:
            if str(data.get(key, '')).strip() == '':
                errors.append(f'Inspection {key.replace("_", " ")} is required.')
        if disposition not in ['Approval for physical signature', 'Not approved']:
            errors.append('Select inspection approval or nonapproval; completion is not approval.')
        if disposition == 'Not approved' and (not data.get('discrepancies') or not data.get('list_delivered')):
            errors.append('Nonapproval requires discrepancies and confirmation that a signed, dated list was given to the owner/operator.')
    if disposition != 'Work documented only' or inspection:
        for key in ['approver', 'certificate_type', 'certificate_number', 'authorization_basis']:
            if not str(data.get(key, '')).strip():
                errors.append(f'{key.replace("_", " ").capitalize()} is required.')
        if data.get('role') == 'Recordkeeping only':
            errors.append('Use the actual authorized person’s role for approval, not a recordkeeping-only identity.')
        if data.get('role') == 'Pilot':
            if data.get('category') != 'Preventive maintenance':
                errors.append('Pilot workflow supports only applicable preventive maintenance.')
            if data.get('performer', '').strip().casefold() != data.get('approver', '').strip().casefold():
                errors.append('Pilot approval requires the pilot to have performed the work personally.')
            if not data.get('pilot_eligible'):
                errors.append('Confirm pilot privileges, owned/operated aircraft, operating restrictions and Appendix A(c) applicability.')
    if data.get('category') in ['Annual inspection', 'Progressive inspection']:
        role = data.get('role')
        if role == 'Mechanic with IA':
            if not data.get('ia_current'):
                errors.append('Confirm current Inspection Authorization and applicable privileges.')
        elif role not in ['Repair station', 'Other authorized person'] or not data.get('authorization_basis'):
            errors.append('Annual/progressive inspection requires IA or a documented applicable alternate authorization; a basic mechanic profile is insufficient.')
    return errors

def elt_status(data,today):
    """14 CFR 91.207(c): cumulative use >1 h OR 50% useful life; applicability user-reviewed."""
    checks=[];missing=False;details=['14 CFR 91.207(c); manufacturer-approved useful life']
    used=quantity(data.get('battery_used'))
    if used is None:missing=True
    else:
        checks.append(3 if used>1 else 1 if used>=Decimal('0.8') else 0)
        details.append(f'Cumulative transmitter use: {used} hours (replacement threshold: more than 1)')
    exempt=data.get('battery_life_exempt',False)
    if exempt and not data.get('battery_exemption_basis'):return 'Unknown','Document the applicable §91.207(c)(2) storage-life exception.'
    if not exempt:
        life=quantity(data.get('battery_life_percent'));expiration=iso_date(data.get('battery_expiration',''))
        if life is None and not expiration:missing=True
        if life is not None:
            checks.append(3 if life>50 else 2 if life==50 else 1 if life>=40 else 0);details.append(f'Useful life expired: {life}%')
        if expiration:
            left=(expiration-today).days;checks.append(3 if left<0 else 2 if left==0 else 1 if left<=30 else 0);details.append('Manufacturer replacement/recharge date: '+str(expiration))
    severity=max(checks,default=0)
    return ('Unknown' if missing and severity<2 else ['Upcoming','Upcoming','Due','Past recorded due threshold'][severity]),'; '.join(details)
