from pathlib import Path
from logbook.ui import MainWindow,RecordDialog,Fields,SetupWizard,PdfPreview
from logbook.documents import write_pdf
from PySide6.QtWidgets import QLineEdit

def test_first_run_wizard_and_navigation(qtbot,store):
    window=MainWindow(store,Path('resources'));qtbot.addWidget(window);window.show()
    assert 'Add your first aircraft' in window.summary.toPlainText()
    wizard=SetupWizard(window);qtbot.addWidget(wizard);assert wizard.pageIds()==[0,1]
    for index in range(13):window.navigation.setCurrentRow(index)
    window.theme('Light');window.theme('Dark')

def test_entry_autosave_reopen_and_pdf_preview(qtbot,store,service,aircraft,entry_data,tmp_path):
    main=MainWindow(store,Path('resources'));qtbot.addWidget(main)
    dialog=RecordDialog(main,'entry');qtbot.addWidget(dialog);dialog.show();dialog.form.set_data(entry_data)
    qtbot.waitUntil(lambda:bool(dialog.record),timeout=4000)
    identity=dialog.record['id'];assert store.get(identity)['data']['performer']=='Test Performer'
    dialog.close()
    ready=service.finalize(store.get(identity));reopened=RecordDialog(main,'entry',ready);qtbot.addWidget(reopened)
    assert not reopened.form.isEnabled()
    output=tmp_path/'preview.pdf';write_pdf(output,[ready],aircraft)
    preview=PdfPreview(output,main);qtbot.addWidget(preview);assert preview.document.pageCount()>0

def test_all_forms_can_save(qtbot,store,service,aircraft):
    main=MainWindow(store,Path('resources'));qtbot.addWidget(main)
    for kind in ['profile','component','item','schedule','ad','sb','part','expense']:
        dialog=RecordDialog(main,kind);qtbot.addWidget(dialog)
        record=dialog.persist();assert record['kind']==kind

def test_preview_does_not_lock_pdf(qtbot,store,service,aircraft,entry_data,tmp_path):
    main=MainWindow(store,Path('resources'));qtbot.addWidget(main)
    record=service.save('entry',entry_data,aircraft['id']);path=tmp_path/'removable.pdf';write_pdf(path,[record],aircraft)
    preview=PdfPreview(path,main);qtbot.addWidget(preview);preview.show();qtbot.wait(50)
    path.unlink();assert preview.document.pageCount()==1
    preview.close()

def test_review_reset_and_timeline(qtbot,store,aircraft):
    main=MainWindow(store,Path('resources'));qtbot.addWidget(main)
    dialog=RecordDialog(main,'entry');qtbot.addWidget(dialog)
    dialog.form.controls['category'].setCurrentText('Annual inspection')
    dialog.form.controls['statement_reviewed'].setChecked(True)
    dialog.form.controls['statement'].setPlainText('Changed actual statement')
    assert not dialog.form.controls['statement_reviewed'].isChecked()
    assert dialog.form.tabs.isTabVisible(2)
    dialog.form.controls['category'].setCurrentText('Preventive maintenance')
    assert not dialog.form.tabs.isTabVisible(2)
    main.navigation.setCurrentRow(13);assert main.kind()=='timeline'
