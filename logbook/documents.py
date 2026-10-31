"""Unicode PDF output and HTML preview from immutable record snapshots."""
from __future__ import annotations
import html
import os
from pathlib import Path
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, HRFlowable,PageBreak
from .storage import now

def font():
    if 'Logbook' not in pdfmetrics.getRegisteredFontNames():
        import reportlab
        fonts = Path(reportlab.__file__).parent / 'fonts'
        pdfmetrics.registerFont(TTFont('Logbook',str(fonts/'Vera.ttf')))
    return 'Logbook'

def text(value):
    return html.escape(str(value)).replace('\n','<br/>')

def sections(record, aircraft):
    d = record['data']
    aircraft = d.get('aircraft_snapshot',aircraft)
    result = [('Aircraft',f"{aircraft['registration']} | {aircraft['data'].get('make','')} {aircraft['data'].get('model','')} | S/N {aircraft['data'].get('serial_number','Not recorded')}"),('Record',record['id']),('Recorded',record.get('created','')),('State',record['state'])]
    if record.get('component_id'):
        result.append(('Component record', record['component_id']))
        component = d.get('component_snapshot',{}).get('data',{})
        if component:
            result.append(('Component identification',' | '.join(component.get(k,'') for k in ['title','manufacturer','model','serial_number'])))
    if record.get('amends_id'):
        result.append(('Amends original',record['amends_id']))
    for key in ['category','date','total_time','tach','hobbs','description','references','parts','performer','extent','inspection_program','discrepancies','source_document','notes','amendment_reason']:
        if str(d.get(key, '')).strip():
            result.append((key.replace('_',' ').capitalize(),d[key]))
    return result

def entry_html(record, aircraft):
    body = ''.join(f'<p><b>{text(k)}</b><br>{text(v)}</p>' for k,v in sections(record,aircraft))
    d = record['data']
    body += '<hr><p><b>Disposition:</b> '+text(d.get('disposition','Work documented only'))+'</p>'
    body += '<p>'+text(d.get('statement',''))+'</p>'
    body += '<p>'+text(' | '.join(d[k] for k in ['approver','certificate_type','certificate_number'] if d.get(k)))+'</p>'
    if d.get('category')=='Historical entry':
        body='<h2>HISTORICAL TRANSCRIPTION</h2><p>Copy of recorded history; not a new maintenance approval. Refer to the original signed source.</p>'+body
    else:body += '<p>Physical signature: __________________________ Date: ______________</p><p><i>Unsigned generated copy. A recorded scan does not electronically sign this document.</i></p>'
    return '<html><body style="font-family:Segoe UI;font-size:11pt;color:#142337;background:white;padding:18px"><h2>Aircraft maintenance record</h2>'+body+'</body></html>'

def write_pdf(path, records, aircraft, compact=False, title='Aircraft maintenance record', font_size=10,compact_width=6.0,discrepancy=False,history=False):
    font_size = max(9,min(int(font_size),14))
    style = ParagraphStyle('body',fontName=font(),fontSize=font_size,leading=font_size*1.45,spaceAfter=7,splitLongWords=True)
    heading = ParagraphStyle('heading',parent=style,fontSize=15,leading=19,textColor=colors.HexColor('#17334b'),spaceAfter=14)
    small = ParagraphStyle('small',parent=style,fontSize=8,leading=11)
    margin = 18 if compact else 42
    width=max(4.0,min(float(compact_width),8.5))*72 if compact else 612
    usable=width-2*margin-12
    temporary = Path(str(path)+'.tmp')
    story=[]
    if history or len(records)!=1:story.append(Paragraph(text(title),heading))
    if not records:
        story.append(Paragraph('No records match this report.',style))
    for index,record in enumerate(records):
        if index:
            story.extend([Spacer(1,12),HRFlowable(width='100%',color=colors.HexColor('#aebbc6')),Spacer(1,12)])
        if record['kind'] == 'entry':
            d = record['data']
            historical=d.get('category')=='Historical entry'
            from .statements import is_inspection
            caption='HISTORICAL TRANSCRIPTION — NOT A NEW APPROVAL' if historical else 'INSPECTION DISCREPANCY LIST' if discrepancy else d.get('category','Maintenance').upper()
            story.append(Paragraph(text(caption),heading if not compact else style))
            identity=dict(sections(record,aircraft))['Aircraft']
            story.append(Paragraph(text(identity),style))
            component=d.get('component_snapshot',{}).get('data',{})
            if component:story.append(Paragraph(text('Component: '+' | '.join(component.get(k,'') for k in ['title','manufacturer','model','serial_number'])),style))
            when=d.get('discrepancy_date') if discrepancy else d.get('date')
            times='  •  '.join(f'{label}: {d[key]}' for key,label in [('total_time','Aircraft TIS'),('tach','Tach'),('hobbs','Hobbs')] if d.get(key) not in (None,''))
            story.append(Paragraph(text(f'Date: {when or "Unknown"}   {times}'),style))
            if record['state'] in ['Draft','Historical import requiring verification']:
                story.append(Paragraph('DRAFT / UNVERIFIED — not signed; not an approval',small))
            if historical:
                story.append(Paragraph('Transcribed historical information only. Consult the original signed record; no new maintenance or approval is represented.',style))
            if discrepancy:
                if not is_inspection(d) or d.get('disposition')!='Not approved':raise ValueError('Discrepancy output requires a nonapproved inspection.')
                story.append(Paragraph('Findings from the linked inspection; unresolved findings are not authorization to operate.',style))
                story.append(Paragraph(text(d.get('discrepancies','No findings entered.')),style))
            else:
                for key,label in [('description',''),('references','Technical references'),('parts','Parts'),('performer','Performed by'),('extent','Inspection extent'),('inspection_program','Inspection program'),('source_document','Historical source / uncertainty'),('notes','Notes'),('amendment_reason','Correction reason')]:
                    if d.get(key):story.append(Paragraph((f'<b>{text(label)}:</b> ' if label else '')+text(d[key]),style))
                for part in d.get('linked_parts_snapshot',[]):
                    story.append(Paragraph(text('Part: '+' | '.join(str(part.get(k,'')) for k in ['title','part_number','serial_number','quantity','action'])),style))
                if record.get('amends_id'):story.append(Paragraph(text('Amendment of record '+record['amends_id']+'; original retained.'),small))
            if historical or history:
                if d.get('statement'):story.append(Paragraph(text('Recorded statement: '+d['statement']),style))
                credentials=' | '.join(str(d[k]) for k in ['approver','certificate_type','certificate_number'] if d.get(k))
                if credentials:story.append(Paragraph(text('Recorded approving person: '+credentials),style))
                if history and not historical:story.append(Paragraph(text('Recorded disposition: '+d.get('disposition','Work documented only')+' | Evidence state: '+record['state']),small))
                story.append(Paragraph(text('Record '+record['id']),small))
                continue
            statement = d.get('statement','')
            if discrepancy:statement='This signed and dated list identifies the discrepancies and unairworthy items associated with the inspection identified above. Its delivery is recorded separately.'
            chunks = [statement[i:i+1800] for i in range(0,len(statement),1800)] or ['']
            for chunk in chunks[:-1]:
                story.append(Paragraph(text(chunk),style))
            block = [Paragraph('Disposition: '+text(d.get('disposition','Work documented only')),style),Paragraph(text(chunks[-1]),style),Paragraph(text(' | '.join(d[k] for k in ['approver','certificate_type','certificate_number'] if d.get(k))),style),Spacer(1,14),Paragraph('Physical signature: ________________________<br/>Date: __________________',style),Paragraph('Unsigned generated copy. Physical signature and actual authorization are required.',small)]
            story.append(KeepTogether(block))
        else:
            story.append(Paragraph(text(record['kind'].upper()+' | '+record['data'].get('title','')),heading))
            for key,value in record['data'].items():
                if value != '' and value is not None:
                    story.append(Paragraph(f'<b>{text(key.replace("_"," ").capitalize())}</b>: {text(value)}',style))
    generated = now()
    height=792
    if compact and len(records)==1:
        measured=0
        for flow in story:
            if isinstance(flow,KeepTogether):
                measured+=sum(child.wrap(usable,100000)[1]+child.getSpaceBefore()+child.getSpaceAfter() for child in flow._content)
            else:measured+=flow.wrap(usable,100000)[1]+flow.getSpaceBefore()+flow.getSpaceAfter()
        height=min(792,max(180,measured+90))
    doc = SimpleDocTemplate(str(temporary),pagesize=(width,height),leftMargin=margin,rightMargin=margin,topMargin=30,bottomMargin=38)
    document_ref=records[0]['id'] if len(records)==1 else 'History / report'
    def footer(canvas, document):
        canvas.setFont('Logbook',6.5)
        canvas.drawString(margin,18,f'Record {document_ref} | Page {document.page}')
        canvas.drawString(margin,9,f'Generated {generated[:19]} UTC • administrative metadata')
        if document.page>1:
            canvas.drawString(margin,height-15,f'{aircraft["registration"]} • continuation • {document_ref}')
    try:
        doc.build(story,onFirstPage=footer,onLaterPages=footer)
        os.replace(temporary,path)
    finally:
        temporary.unlink(missing_ok=True)
