from logbook.documents import sections

def test_finalized_identification_is_snapshot(service,store,aircraft,entry_data):
    record=service.finalize(service.save('entry',entry_data,aircraft['id']))
    changed=service.save_aircraft({**aircraft['data'],'registration':'CHANGED'},aircraft)
    rendered=dict(sections(store.get(record['id']),changed))
    assert 'TEST-ONLY' in rendered['Aircraft'] and 'CHANGED' not in rendered['Aircraft']
    amended=service.amend(record,'Test correction')
    assert 'aircraft_snapshot' not in amended['data']
