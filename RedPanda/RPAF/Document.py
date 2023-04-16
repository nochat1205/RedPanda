from OCC.Core.TDocStd import TDocStd_Document

__all__ = ['Document']
def doc_str(doc):
    try:
        name = doc.GetName()
    except:
        name = 'UnSaved'
    return name

Document = TDocStd_Document
Document.__str__ = doc_str
Document.__repr__ = doc_str
