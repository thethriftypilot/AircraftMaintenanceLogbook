import csv
import json
import zipfile
from pathlib import Path
import pytest
from pypdf import PdfReader
from logbook.backup import backup,inspect_backup,restore
from logbook.documents import write_pdf
from logbook.portability import import_csv,export_csv,export_json,read_csv

def pdf_file(tmp_path):
    from reportlab.pdfgen.canvas import Canvas
    path=tmp_path/'signed-test.pdf';c=Canvas(str(path));c.drawString(50,700,'TEST ONLY supporting document');c.save();return path

def test_signed_copy_preservation(service,store,aircraft,entry_data,tmp_path):
    record=service.finalize(service.save('entry',entry_data,aircraft['id']))
    with pytest.raises(ValueError):service.transition(record,'Signed copy recorded','Tester','missing')
    attachment=service.attach(record['id'],pdf_file(tmp_path))
    record=service.transition(record,'Signed copy recorded','Test recorder',attachment)
    assert record['state']=='Signed copy recorded'
    attached=service.attachments(record['id'])[0]
    assert service.verify_attachment(attached)
    with pytest.raises(Exception):service.remove_attachment(attached)
    (store.root/'attachments'/attached['stored_name']).write_bytes(b'changed')
    assert not service.verify_attachment(attached)

def test_safe_attachments(service,aircraft,entry_data,tmp_path):
    record=service.save('entry',entry_data,aircraft['id'])
    bad=tmp_path/'bad.pdf';bad.write_text('executable')
    with pytest.raises(ValueError):service.attach(record['id'],bad)
    bad=tmp_path/'bad.exe';bad.write_bytes(b'%PDF-1.0')
    with pytest.raises(ValueError):service.attach(record['id'],bad)

def test_backup_restore_and_recovery(service,store,aircraft,entry_data,tmp_path):
    record=service.save('entry',entry_data,aircraft['id']);service.attach(record['id'],pdf_file(tmp_path))
    path=backup(store,tmp_path/'backup.zip');info=inspect_backup(path)
    assert info['aircraft_count']==1
    service.save_aircraft({'registration':'AFTER-BACKUP'})
    with pytest.raises(ValueError):restore(store,path)
    restore(store,path,True)
    assert len(store.aircraft())==1 and store.integrity()
    assert service.verify_attachment(service.attachments(record['id'])[0])
    assert list((store.root/'backups').glob('pre-restore-*.zip'))

@pytest.mark.parametrize('name',['../evil','/absolute','attachments/../../evil','C:/evil','attachments\\evil'])
def test_traversal_rejected(tmp_path,name):
    path=tmp_path/'bad.zip'
    with zipfile.ZipFile(path,'w') as archive:archive.writestr(name,'bad')
    with pytest.raises(ValueError):inspect_backup(path)

def test_corrupt_backup_rejected(store,tmp_path):
    good=backup(store,tmp_path/'good.zip');bad=tmp_path/'bad.zip'
    with zipfile.ZipFile(good) as source,zipfile.ZipFile(bad,'w') as target:
        for name in source.namelist():target.writestr(name,b'corrupt' if name=='logbook.db' else source.read(name))
    with pytest.raises(ValueError):inspect_backup(bad)

@pytest.mark.parametrize('compact',[False,True])
def test_long_pdf_pages_and_signature(service,aircraft,entry_data,tmp_path,compact):
    text='TEST ONLY: José replaced fictional part & inspected <test>. '*500
    record=service.save('entry',{**entry_data,'description':text,'statement':'TEST ONLY certification.','notes':'END-OF-CONTENT'},aircraft['id'])
    path=tmp_path/'long.pdf';write_pdf(path,[record],aircraft,compact)
    reader=PdfReader(path);joined=''.join(p.extract_text() for p in reader.pages)
    assert len(reader.pages)>2 and 'END-OF-CONTENT' in joined and 'Unsigned generated copy' in joined
    assert 'Physical signature' in reader.pages[-1].extract_text()
    assert all(p.mediabox.width==(432 if compact else 612) for p in reader.pages)
    assert '/Font' in reader.pages[0]['/Resources']

def test_csv_transaction_and_special_characters(store,aircraft,tmp_path):
    rows=[{'when':'2026-01-01','work':'José, test\nline two'},{'when':'bad','work':'no'}]
    mapping={'date':'when','description':'work'}
    with pytest.raises(ValueError):import_csv(store,aircraft['id'],rows,mapping,'test.csv')
    assert not store.records('entry')
    assert import_csv(store,aircraft['id'],rows[:1],mapping,'test.csv')==1
    record=store.records('entry')[0];assert record['state']=='Historical import requiring verification'
    output=tmp_path/'out.csv';export_csv([record],output)
    _,parsed=read_csv(output);assert parsed[0]['description']=='José, test\nline two'
    output=tmp_path/'out.json';export_json(store,output)
    data=json.loads(output.read_text(encoding='utf-8'));assert data['schema']==1 and len(data['records'])==1

def test_empty_export(store,tmp_path):
    export_csv([],tmp_path/'empty.csv');assert read_csv(tmp_path/'empty.csv')[1]==[]
    export_json(store,tmp_path/'empty.json');assert json.loads((tmp_path/'empty.json').read_text())['records']==[]
