from OCC.Core.TDocStd import TDocStd_Document

__all__ = ['Document']
def doc_str(doc):
    try:
        name = doc.GetName()
    except:
        name = 'UnSaved'
    return name

def File(doc):
    if 'url' not in doc.__dict__:
        return None
    return doc.url

def SetFile(doc, fileUrl):
    doc.url = fileUrl


Document = TDocStd_Document
Document.__str__ = doc_str
Document.__repr__ = doc_str
Document.File = File
Document.SetFile = SetFile
