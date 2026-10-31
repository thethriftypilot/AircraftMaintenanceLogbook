"""Explicitly requested draft language; never applied without user review."""
import re

def is_inspection(data):
    return 'inspection' in data.get('category','').lower() and data.get('category')!='Inspection/test documentation'

def inspection_statement(data):
    if not is_inspection(data):raise ValueError('Select an inspection category first.')
    category=data['category'];outcome=data.get('disposition')
    if outcome not in ['Approval for physical signature','Not approved']:raise ValueError('Select the actual inspection disposition first.')
    if category=='Progressive inspection':
        if not data.get('routine_scope') or not data.get('detailed_scope'):raise ValueError('Identify routine and detailed inspection portions before preparing a statement.')
        result=f"I certify that in accordance with a progressive inspection program, a routine inspection of {data['routine_scope']} and a detailed inspection of {data['detailed_scope']} were performed and the aircraft or components are {'approved' if outcome=='Approval for physical signature' else 'disapproved'} for return to service."
    elif outcome=='Approval for physical signature':
        result=f'I certify that this aircraft has been inspected in accordance with {category.lower()} and was determined to be in airworthy condition.'
    else:
        result=f'I certify that this aircraft has been inspected in accordance with {category.lower()}.'
    if outcome=='Not approved':
        if not data.get('discrepancy_date'):raise ValueError('Enter the date of the signed discrepancy list.')
        result+=f" A list of discrepancies and unairworthy items dated {data['discrepancy_date']} has been provided to the aircraft owner or operator."
    return result

def review_errors(data):
    if not is_inspection(data):return []
    errors=[];statement=' '.join(data.get('statement','').lower().split())
    if not data.get('statement_reviewed') or not data.get('statement_reviewer','').strip():
        errors.append('Identify the statement reviewer and confirm its meaning matches the actual inspection outcome, extent, program and discrepancy delivery. This is not verified authority.')
    if any(marker in statement for marker in ['[insert','<insert','todo','test only certification']):errors.append('Replace unfinished or demonstration certification text.')
    if data.get('category')=='Progressive inspection':
        if not all(data.get(k,'').strip() for k in ['routine_scope','detailed_scope','inspection_program']):errors.append('Progressive inspection requires program, routine scope and detailed scope.')
        if not all(word in statement for word in ['routine','detailed','progressive']):errors.append('Progressive statement must identify routine and detailed inspection under the program.')
    elif 'inspected' not in statement:errors.append('Inspection statement must describe the inspection performed.')
    if data.get('disposition')=='Approval for physical signature':
        if any(word in statement for word in ['not approved','disapproved','unairworthy']):errors.append('Statement contradicts the selected approval outcome.')
        if data.get('category')!='Progressive inspection' and 'airworthy condition' not in statement:errors.append('Approval statement must convey the actual airworthy-condition determination under §43.11(a)(4).')
    elif data.get('disposition')=='Not approved':
        if 'airworthy condition' in statement or re.search(r'(?<!not )(?<!dis)approved for return',statement):errors.append('Nonapproval statement must not assert approval or an airworthy-condition finding.')
        if not all(word in statement for word in ['list','discrepancies','provided']) or not any(word in statement for word in ['owner','operator']):errors.append('Nonapproval statement must convey that the discrepancy list was provided to the owner/operator.')
        if not data.get('discrepancy_date') or data.get('discrepancy_date') not in data.get('statement',''):errors.append('Nonapproval statement must identify the discrepancy-list date.')
    return errors
