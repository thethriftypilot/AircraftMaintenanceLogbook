"""Declarative field descriptions used by native accessible forms."""
from .domain import CATEGORIES, ROLES

def fields(names):
    return [(x, x.replace('_',' ').capitalize(), 'text') for x in names.split()]

SCHEDULE = [('applicability','Applicability',['Unknown','Under review','Applicable','Not applicable'])] + fields('rationale last_date months due_date time_source last_hours interval_hours due_hours last_cycles interval_cycles due_cycles lead_days lead_hours lead_cycles') + [('calendar_month','Use end of calendar month','bool'),('completed','One-time task completed','bool'),('notes','Requirements / applicability notes','long')]
FORMS = {
 'aircraft': [ ('Aircraft', fields('registration make model serial_number year category airworthiness owner base_airport country inspection_program') + [('archived','Archive aircraft (retain records)','bool')]), ('Operating time', fields('total_time tach hobbs cycles time_source last_date last_annual') + [('notes','Operating notes','long')])],
 'profile': [('Identity', fields('name') + [('role','Role',ROLES)] + fields('certificate_type certificate_number ratings authorization_until business contact') + [('ia_current','IA current (user provided)','bool'),('authorization_basis','Authorization / limitations','long')])],
 'component': [('Component', [('title','Component name','text'),('type','Type',['Airframe','Engine','Propeller','Avionics','Appliance','Other'])] + fields('manufacturer model serial_number installation_date removal_date total_time since_overhaul since_installation cycles') + [('notes','Overhaul / service limits / installation details','long')])],
 'component_event': [('History event', [('action','Action',['Installed','Removed','Overhauled','Correcting event'])] + fields('date total_time') + [('notes','Event details / correction reference','long')])],
 'entry': [
  ('Work', [('category','Entry category',CATEGORIES)] + fields('date total_time tach hobbs performer') + [('description','Actual work performed (multiple actions welcome)','long'),('references','Technical data / maintenance references','long'),('parts','Parts installed / removed (numbers, serials, quantity)','long')]),
  ('Approval', [('role','Approving person role',ROLES),('disposition','Disposition',['Work documented only','Approval for physical signature','Not approved'])] + fields('approver certificate_type certificate_number ratings') + [('authorization_basis','Applicable authorization / privileges','long'),('ia_current','I confirm current IA privileges where applicable','bool'),('pilot_eligible','I verified pilot privileges, own/operate eligibility, operating restrictions and Appendix A(c)','bool'),('affirmed','I affirm the actual facts, record accuracy and applicable authorization','bool')]),
  ('Inspection', [('extent','Inspection extent / portions accomplished','long'),('inspection_program','Inspection program and procedures (if applicable)','long'),('statement','Certification statement appropriate to actual outcome (§ 43.11)','long'),('discrepancies','Discrepancies / unairworthy items','long'),('list_delivered','Signed and dated discrepancy list given to owner/operator','bool')]),
  ('Source and notes', [('source_document','Historical source / uncertainty','long'),('notes','Notes / work order / invoice','long'),('amendment_reason','Amendment reason','long')])],
 'item': [('Maintenance item', fields('title date identified_by assigned_to') + [('priority','Priority',['Normal','Low','High','Urgent']),('status','Status',['Open','Planned','In progress','Awaiting parts','Work completed / awaiting approval','Deferred','Canceled','Closed']),('description','Description','long')] + fields('due_date due_hours parts') + [('completion_notes','Completion documentation / deferral rationale','long'),('notes','Notes','long')])],
 'schedule': [('Schedule', fields('title') + SCHEDULE)],
 'ad': [('Directive', fields('title number revision authority') + [('requirements','Compliance requirements','long'),('method','Compliance method','long'),('next_action','Next required action','long')]),('Tracking', SCHEDULE)],
 'sb': [('Service bulletin', fields('title number revision manufacturer') + [('status','Status',['Under review','Recommended','Mandatory by separate basis','Accomplished','Not applicable']),('basis','Mandatory basis, if any (do not infer from publication)','long'),('notes','Requirements / compliance / notes','long')])],
 'part': [('Part', fields('title part_number serial_number manufacturer quantity unit_cost currency supplier date') + [('action','Action',['Purchased','Installed','Removed','Returned']),('notes','Eligibility evidence / receipt / notes','long')])],
 'expense': [('Expense', fields('title date amount currency vendor invoice') + [('category','Category',['Parts','Labor','Consumables','Inspections','Outside services','Miscellaneous']),('status','Payment status',['Unpaid','Paid','Partial'])] + fields('labor_hours labor_rate') + [('notes','Notes','long')])],
}

# Time sources are explicit; tach, Hobbs and component hours are never substituted.
for kind in ['schedule','ad']:
    FORMS[kind] = [(title,[(key,label,['total_time','tach','hobbs','since_overhaul','since_installation']) if key=='time_source' else (key,label,typ) for key,label,typ in definitions]) for title,definitions in FORMS[kind]]

FORMS['entry'][2][1].extend(fields('statement_reviewer discrepancy_date routine_scope detailed_scope')+[('statement_reviewed','I reviewed the statement’s meaning and actual outcome','bool')])
FORMS['component'][0][1].insert(1,('installation_status','Installation state',['Unknown','Installed','Removed']))
FORMS['schedule'].append(('Applicability & ELT',[
 ('schedule_type','Reminder type',['Custom','Annual','100-hour','ELT inspection','ELT battery','Altimeter/static','Transponder']),
 ('applicability_confirmed','I reviewed applicability for this aircraft and operation','bool'),
 ('source_reference','Current controlling source / approved data','long'),
 ('baseline_reference','Qualifying event / baseline evidence','long'),
 ('time_basis','Time-in-service basis (if using another meter)','long'),
 ('exception_basis','Inspection-program or operating exception / limitations','long'),
 ('exception_reviewed','I independently reviewed this exception and configured appropriate limits','bool'),
 ('excess_hours','100-hour excess used en route (subtract from next interval)','text'),
 ('battery_used','Cumulative ELT transmitter use (hours)','text'),
 ('battery_life_percent','Manufacturer useful life expired (%)','text'),
 ('battery_expiration','Manufacturer battery replacement/recharge date','text'),
 ('battery_life_exempt','Battery qualifies for §91.207(c)(2) storage-life exception','bool'),
 ('battery_exemption_basis','Battery exception basis','long')]))
