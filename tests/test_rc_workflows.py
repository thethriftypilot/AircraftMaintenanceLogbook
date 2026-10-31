from datetime import date
import json,zipfile
import pytest
from pypdf import PdfReader
from logbook.statements import inspection_statement,review_errors
from logbook.domain import schedule_status
from logbook.documents import write_pdf
from logbook.reports import expense_summary,labor_amount,export_aircraft
from logbook.backup import inspect_backup
from test_files import pdf_file

def inspection(entry_data,approved=True):
    d={**entry_data,'category':'Annual inspection','role':'Mechanic with IA','ia_current':True,'extent':'Annual scope','total_time':'100.1','statement_reviewed':True,'statement_reviewer':'Fictional reviewer','discrepancy_date':'2026-10-01','discrepancies':'Fictional cabin-light defect','list_delivered':True,'disposition':'Approval for physical signature' if approved else 'Not approved'}
    d['statement']=inspection_statement(d)
    return d

@pytest.mark.parametrize('approved',[True,False])
def test_outcome_review(entry_data,approved):
    d=inspection(entry_data,approved);assert not review_errors(d)
    d['disposition']='Not approved' if approved else 'Approval for physical signature'
    assert review_errors(d)

def test_delivery_content_evidence_binding(service,aircraft,entry_data,tmp_path):
    d=inspection(entry_data,False);r=service.save('entry',d,aircraft['id'])
    with pytest.raises(ValueError,match='delivery'):service.finalize(r)
    a=service.attach(r['id'],pdf_file(tmp_path));service.record_delivery(r['id'],a,'Fictional owner','2026-10-01','Tester')
    r=service.save('entry',{**d,'discrepancies':'Changed findings'},aircraft['id'],r)
    with pytest.raises(ValueError,match='changed after delivery'):service.finalize(r)
    service.record_delivery(r['id'],a,'Fictional owner','2026-10-01','Tester')
    assert service.finalize(r)['state']=='Ready to print'

def test_cross_record_delivery_rejected(service,aircraft,entry_data,tmp_path):
    r=service.save('entry',inspection(entry_data,False),aircraft['id']);other=service.save('entry',entry_data,aircraft['id'])
    a=service.attach(other['id'],pdf_file(tmp_path))
    with pytest.raises(ValueError,match='belong'):service.record_delivery(r['id'],a,'Owner','2026-10-01','Tester')

def test_closure_rechecks_disk_evidence(service,store,aircraft,entry_data,tmp_path):
    r=service.finalize(service.save('entry',entry_data,aircraft['id']));a=service.attach(r['id'],pdf_file(tmp_path));r=service.transition(r,'Signed copy recorded','Tester',a)
    (store.root/'attachments'/service.attachments(r['id'])[0]['stored_name']).unlink()
    with pytest.raises(ValueError,match='missing or changed'):service.save('item',{'status':'Closed','completion_notes':'Corrected'},aircraft['id'],entry_id=r['id'])

def test_history_and_compact_pdf(service,aircraft,entry_data,tmp_path):
    r=service.save('entry',{**entry_data,'statement':'Recorded test statement'},aircraft['id'])
    path=tmp_path/'short.pdf';write_pdf(path,[r],aircraft,compact=True,compact_width=5)
    pdf=PdfReader(path);assert len(pdf.pages)==1 and pdf.pages[0].mediabox.width==360 and pdf.pages[0].mediabox.height<792
    assert 'Physical signature' in pdf.pages[0].extract_text()
    write_pdf(path,[r],aircraft,history=True);text=PdfReader(path).pages[0].extract_text();assert 'Recorded test statement' in text and 'Physical signature' not in text
    r['data'].update(category='Historical entry',source_document='Fictional original page')
    write_pdf(path,[r],aircraft);text=PdfReader(path).pages[0].extract_text();assert 'HISTORICAL TRANSCRIPTION' in text and 'Physical signature' not in text

def test_selected_export_scoped_and_not_backup(service,store,aircraft,entry_data,tmp_path):
    other=service.save_aircraft({'registration':'EXCLUDED-AIRCRAFT'});service.save('entry',entry_data,other['id'])
    r=service.save('entry',entry_data,aircraft['id']);service.attach(r['id'],pdf_file(tmp_path))
    path=tmp_path/'handover.zip';export_aircraft(store,aircraft['id'],path)
    with zipfile.ZipFile(path) as archive:
        payload=json.loads(archive.read('records.json'));assert len(payload['records'])==1 and not payload['restorable']
        assert 'EXCLUDED-AIRCRAFT' not in archive.read('records.json').decode()
        assert any(n.startswith('attachments/') for n in archive.namelist())
    with pytest.raises(ValueError):inspect_backup(path)

def test_decimal_currency_and_labor():
    records=[{'kind':'expense','data':{'amount':v,'currency':currency,'date':'2026-01-01'}} for v,currency in [('0.1','USD'),('0.2','USD'),('1.00','CAD')]]
    assert expense_summary(records)==[{'currency':'CAD','group':'2026','amount':'1.00'},{'currency':'USD','group':'2026','amount':'0.3'}]
    assert labor_amount('1.25','80.02')=='100.0250'

def test_currency_required(service,aircraft):
    with pytest.raises(ValueError,match='currency'):service.save('expense',{'amount':'5'},aircraft['id'])

@pytest.mark.parametrize('used,life,status',[('1','20','Upcoming'),('1.01','20','Past recorded due threshold'),('0','50','Due'),('0','51','Past recorded due threshold'),('','','Unknown')])
def test_elt_thresholds(used,life,status):
    d={'schedule_type':'ELT battery','applicability':'Applicable','applicability_confirmed':True,'source_reference':'91.207(c)','baseline_reference':'Fictional manufacturer data','battery_used':used,'battery_life_percent':life}
    assert schedule_status(d,{},date(2026,10,1))[0]==status

def test_timing_and_exception_conservative():
    d={'schedule_type':'100-hour','applicability':'Applicable','applicability_confirmed':True,'source_reference':'91.409(b)','baseline_reference':'Fictional last inspection','last_hours':'100','interval_hours':'100','time_source':'tach','excess_hours':'5'}
    assert schedule_status(d,{'tach':'195'})[0]=='Unknown'
    d.update(time_source='total_time');assert schedule_status(d,{'total_time':'195'})[0]=='Due'
    d['exception_basis']='User-proposed program';assert schedule_status(d,{'total_time':'195'})[0]=='Unknown'

def test_amendments_and_page(service,store,aircraft,entry_data):
    original=service.finalize(service.save('entry',entry_data,aircraft['id']));amendment=service.amend(original,'Correct fictional part number')
    assert [r['id'] for r in service.amendment_chain(amendment['id'])]==[original['id'],amendment['id']]
    assert store.get(original['id'])==original
    for i in range(104):service.save('item',{'title':f'searchable {i}'},aircraft['id'])
    rows,count=store.page('item',aircraft['id'],'searchable',100,100);assert count==104 and len(rows)==4
