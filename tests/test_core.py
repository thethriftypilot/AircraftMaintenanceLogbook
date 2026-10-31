import json
import sqlite3
from datetime import date
from decimal import Decimal
from pathlib import Path
import pytest
from logbook.domain import calendar_due,schedule_status,quantity,validate_entry
from logbook.services import Service
from logbook.storage import Store

def test_aircraft_persistence_duplicates_and_revision(service,store,aircraft):
    with pytest.raises(sqlite3.IntegrityError):service.save_aircraft({'registration':'test-only'})
    second=service.save_aircraft({'registration':'SECOND-TEST'})
    changed=service.save_aircraft({**aircraft['data'],'tach':'55.2'},aircraft)
    assert changed['revision']==2
    with pytest.raises(ValueError):service.save_aircraft(aircraft['data'],aircraft)
    assert len(Store(store.root).aircraft())==2
    assert store.integrity()

@pytest.mark.parametrize('value',['NaN','Infinity','-1','bogus'])
def test_bad_quantities(value):
    with pytest.raises(ValueError):quantity(value)

def test_decimal_exact():assert quantity('0.1')+quantity('0.2')==Decimal('0.3')

def test_draft_finalize_amend(service,store,aircraft,entry_data):
    record=service.save('entry',entry_data,aircraft['id'])
    other=dict(record)
    record=service.save('entry',{**entry_data,'notes':'Second session'},aircraft['id'],record)
    with pytest.raises(ValueError):service.save('entry',entry_data,aircraft['id'],other)
    record=service.finalize(record)
    with pytest.raises(ValueError):service.save('entry',entry_data,aircraft['id'],record)
    with pytest.raises(sqlite3.IntegrityError):
        with store.connect() as con:con.execute('UPDATE records SET data=? WHERE id=?',('{}',record['id']))
    with pytest.raises(sqlite3.IntegrityError):
        with store.connect() as con:con.execute("UPDATE records SET state='Draft' WHERE id=?",(record['id'],))
    amendment=service.amend(record,'Correct transcribed detail')
    assert amendment['amends_id']==record['id'] and amendment['state']=='Draft'
    assert store.get(record['id'])['data']['notes']=='Second session'
    with pytest.raises(sqlite3.IntegrityError):
        with store.connect() as con:con.execute('DELETE FROM records WHERE id=?',(record['id'],))

def test_requirements_and_work_only(entry_data):
    assert not validate_entry(entry_data)
    assert validate_entry({})
    assert validate_entry({**entry_data,'certificate_number':''})
    assert not validate_entry({**entry_data,'disposition':'Work documented only','certificate_number':''})
    assert validate_entry({**entry_data,'affirmed':False})

def inspection(entry_data):
    return {**entry_data,'category':'Annual inspection','extent':'Test extent','total_time':'100','statement':'I certify this aircraft has been inspected in accordance with an annual inspection and was determined to be in airworthy condition.','statement_reviewer':'Fictional test reviewer','statement_reviewed':True,'role':'Mechanic with IA','ia_current':True}

def test_inspection_authority_and_nonapproval(entry_data):
    data=inspection(entry_data)
    assert not validate_entry(data)
    assert validate_entry({**data,'role':'Mechanic'})
    assert validate_entry({**data,'ia_current':False})
    assert validate_entry({**data,'total_time':''})
    assert validate_entry({**data,'disposition':'Work documented only'})
    assert validate_entry({**data,'disposition':'Not approved'})
    assert not validate_entry({**data,'disposition':'Not approved','discrepancies':'TEST ONLY broken item','list_delivered':True,'discrepancy_date':'2026-10-01','statement':'I certify this aircraft was inspected in accordance with an annual inspection. A list of discrepancies and unairworthy items dated 2026-10-01 has been provided to the owner.'})

def test_pilot_safeguards(entry_data):
    data={**entry_data,'role':'Pilot','category':'Preventive maintenance','performer':'Test Approver','pilot_eligible':True}
    assert not validate_entry(data)
    assert validate_entry({**data,'performer':'Other person'})
    assert validate_entry({**data,'category':'Repair'})
    assert validate_entry({**data,'pilot_eligible':False})

def test_historical_preserves_unknown(service,aircraft):
    record=service.save('entry',{'category':'Historical entry','description':'Transcribed uncertain event','source_document':'Paper page 1, date illegible'},aircraft['id'])
    assert record['state']=='Historical import requiring verification'
    assert not validate_entry(record['data'])
    assert 'date' not in record['data']

def test_cross_aircraft_links(service,aircraft,entry_data):
    other=service.save_aircraft({'registration':'OTHER'})
    component=service.save('component',{'title':'Engine A'},aircraft['id'])
    entry=service.save('entry',entry_data,aircraft['id'])
    with pytest.raises(ValueError):service.save('entry',entry_data,other['id'],component_id=component['id'])
    with pytest.raises(ValueError):service.save('item',{'title':'Squawk'},other['id'],entry_id=entry['id'])

def test_component_transfer_keeps_original(service,store,aircraft,entry_data):
    other=service.save_aircraft({'registration':'OTHER'})
    component=service.save('component',{'title':'Engine A','serial_number':'DEMO-ENG'},aircraft['id'])
    entry=service.save('entry',entry_data,aircraft['id'],component_id=component['id'])
    service.transfer_component(component,other['id'],'2026-10-02','TEST ONLY transfer')
    assert store.get(component['id'])['aircraft_id']==other['id']
    assert store.get(entry['id'])['aircraft_id']==aircraft['id']
    assert len(store.records('component_event'))==2
    service.save('entry',entry_data,aircraft['id'],entry,component_id=component['id'])

@pytest.mark.parametrize('start,months,expected',[('2024-02-29',12,'2025-02-28'),('2025-01-31',1,'2025-02-28'),('2025-12-01',2,'2026-02-28'),('2023-02-01',12,'2024-02-29')])
def test_calendar_months(start,months,expected):assert calendar_due(date.fromisoformat(start),months).isoformat()==expected

def test_earlier_threshold_unknown_and_source():
    d={'applicability':'Applicable','last_date':'2025-10-01','months':'12','calendar_month':True,'interval_hours':'100','last_hours':'10','time_source':'tach'}
    assert schedule_status(d,{'tach':'111','total_time':'1'},date(2026,1,1))[0]=='Past recorded due threshold'
    assert schedule_status(d,{'tach':'110'},date(2026,1,1))[0]=='Due'
    assert schedule_status(d,{'total_time':'110'},date(2026,1,1))[0]=='Unknown'
    assert schedule_status(d,{},date(2026,11,1))[0]=='Past recorded due threshold'
    assert schedule_status({**d,'applicability':'Not applicable'},{})[0]=='Not configured'
    assert schedule_status({'applicability':'Unknown'},{})[0]=='Unknown'

def test_cycles():
    assert schedule_status({'applicability':'Applicable','last_cycles':'10','interval_cycles':'30'},{'cycles':'40'})[0]=='Due'

def test_audit_append_only(service,store,aircraft,entry_data):
    record=service.save('entry',entry_data,aircraft['id'])
    with pytest.raises(sqlite3.IntegrityError):
        with store.connect() as con:con.execute('DELETE FROM audit')
    with store.connect() as con:assert con.execute('SELECT count(*) FROM audit WHERE entity_id=?',(record['id'],)).fetchone()[0]==1

def test_ad_rationale(service,aircraft):
    with pytest.raises(ValueError):service.save('ad',{'applicability':'Not applicable'},aircraft['id'])

def test_closure_needs_evidence(service,aircraft):
    with pytest.raises(ValueError):service.save('item',{'title':'Test','status':'Closed'},aircraft['id'])

def test_newer_database_refused(tmp_path):
    path=tmp_path/'new';path.mkdir()
    with sqlite3.connect(path/'logbook.db') as con:con.execute('PRAGMA user_version=999')
    with pytest.raises(ValueError):Store(path)

def test_interrupted_transaction_rolls_back(store):
    with pytest.raises(RuntimeError):
        with store.connect() as con:
            con.execute("INSERT INTO settings VALUES('test','1')")
            raise RuntimeError('simulated interruption')
    assert store.setting('test') is None
