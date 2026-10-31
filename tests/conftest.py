import os
# Headless Qt avoids workstation accessibility/COM clients interfering with tests.
# Native Windows rendering is exercised separately by visual_evidence.py and packaged launch.
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from logbook.storage import Store
from logbook.services import Service

@pytest.fixture
def store(tmp_path):return Store(tmp_path/'data')
@pytest.fixture
def service(store):return Service(store)
@pytest.fixture
def aircraft(service):return service.save_aircraft({'registration':'TEST-ONLY','make':'Fictional','model':'Test','total_time':'100.1'})
@pytest.fixture
def entry_data():return {'category':'General maintenance','date':'2026-10-01','description':'TEST ONLY: replaced fictional part.','performer':'Test Performer','approver':'Test Approver','role':'Mechanic','certificate_type':'A&P','certificate_number':'TEST-NOT-VALID','authorization_basis':'Fictional test only','disposition':'Approval for physical signature','affirmed':True}
