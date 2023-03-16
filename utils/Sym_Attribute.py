import inspect

from OCC.Core.Standard import (
    Standard_GUID
)
from OCC.Core.TDataStd import TDataStd_TreeNode
from OCC.Core.TDF import (
    TDF_Attribute,
    TDF_Label,
    TDF_AttributeIterator
)

from utils.GUID import (
    IDcolCurvGUID,
    IDcolGUID,
    IDcolSurfGUID,
    AssemblyGUID,
    ShapeRefGUID,
    Sym_ArrayPntGUID,
    Sym_IdAttr_GUID
)
from OCC.Core.TFunction import TFunction_Function
from utils.logger import Logger



class Assembly(TDataStd_TreeNode):
    def GetID():
        return AssemblyGUID

class Sym_ShapeRef(TDataStd_TreeNode):
    """
    label0 ref Label1.Shape
    => label0 is Label1.Shape
    """

    def SetReference(self, theLabel):
        father = Sym_ShapeRef.Set(theLabel)
        father.Append(Sym_ShapeRef)

    def Get(self):
        father = self.Father()
        if father:
            return father.Label()
        return None

    @staticmethod
    def Set(aLabel, theRefedLabel=None)->TDataStd_TreeNode:
        TN_self = TDataStd_TreeNode.Set(aLabel, Sym_ShapeRef.GetID())
        TN_self.__class__ = Sym_ShapeRef
        if theRefedLabel:
            father = Sym_ShapeRef.Set(theRefedLabel)
            father.Append(TN_self)
        return TN_self

    @staticmethod
    def GetID():
        return ShapeRefGUID

    def __iter__(self):
        self.it = self.First()
        return self

    def __next__(self):
        if self.it is None:
            raise StopIteration

        node = self.it
        self.it = node.Next()
        return node.Label()

class Sym_GuidAttr(TFunction_Function):
    @staticmethod
    def GetID():
        return Sym_IdAttr_GUID


class IDcol(TDataStd_TreeNode):
    def GetID():
        return IDcolGUID

class IDcolSurf(TDataStd_TreeNode):
    def GetID():
        return IDcolSurfGUID

class IDcolCurv(TDataStd_TreeNode):
    def GetID():
        return IDcolCurvGUID

