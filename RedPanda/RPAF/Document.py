from OCC.Core.TDocStd import TDocStd_Document

__all__ = ['Document']
def doc_str(doc):
    try:
        name = doc.GetName()
    except:
        name = 'UnSaved'
    return name

def SetName(doc, name):
    doc.name = name

def GetName(doc):
    return doc.name

def File(doc):
    return doc.url

def SetFile(doc, fileUrl):
    doc.url = fileUrl

Document = TDocStd_Document
Document.__str__ = doc_str
Document.__repr__ = doc_str
# Document.SetName = SetName
# Document.GetName = GetName
Document.url = None
Document.File = File
Document.SetFile = SetFile
