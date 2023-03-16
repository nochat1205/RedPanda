from OCC.Core.TDF import TDF_Label

from utils.OCCUtils import (
    TFunction_Function, 
    TFunction_DriverTable,
    Standard_GUID
)
from utils.Driver.Sym_Driver import (
    Sym_Driver,
    Argument,
    GetDriver,
    Param
)
from utils.GUID import *

from utils.logger import Logger


class ArrayParam():
    def __init__(self, subParam:dict, theSize:int=0) -> None:
        self._subParam = subParam
        self._size = theSize

    def __str__(self) -> str:
        return f'Array sz:{self._size} subParam: {self._subParam}'

    def __repr__(self) -> str:
        return self.__str__()

class Sym_NewBuilder(object):
    """_summary_

    Args:
        param (dict): {"type":, "default":value}
    """
    def __init__(self, aDriver:Sym_Driver, parent=None) -> None:
        Logger().info('Start init NewParamBuilder ')
        Logger().info(f"Type:{aDriver.Type} Driver:{aDriver.ID}")

        self.type = aDriver.Type
        self.TFunctionID = aDriver.ID
        self.name_param = Param(str, "shape")
        self.parent_param = Param(str, "0:1")

        self.shape_param:dict = self.GetDefination(aDriver)
        Logger().info(f'name:{self.name_param}')
        Logger().info(f'parent:{self.parent_param}')
        Logger().info(f'shape:{self.shape_param}')
        Logger().info('End init NewParamBuilder ')

    @staticmethod
    def GetParamWith(aDriver: Sym_Driver):
        def GetParamDefault(aDriver:Sym_Driver):
            if len(aDriver.Arguments) > 0: # read children
                child_ParamDict = {}
                for name, param in aDriver.Arguments.items():
                    param:Argument
                    child_param = Sym_NewBuilder.GetParamWith(
                            GetDriver(param.DriverID)
                        )
                    child_ParamDict[name] = child_param
                return child_ParamDict
            else: # read leave value
                Attri = aDriver.Attributes['value']
                return Attri

        def GetArrayParam(aDriver:Sym_Driver):
            subDriver = GetDriver(aDriver._SubTypeId)
            return ArrayParam(GetParamDefault(subDriver))

        param = None
        if aDriver.ID == Sym_ArrayDriver_GUID:
            param = GetArrayParam(aDriver)
        else:
            param = GetParamDefault(aDriver)
        return param

    @staticmethod
    def GetDefination(aDriver:Sym_Driver):
        return Sym_NewBuilder.GetParamWith(aDriver)

class Sym_ChangeBuilder(object):
    def __init__(self, aLabel: TDF_Label):
        Logger().info('Start init ChangeParamBuilder ')
        Logger().info(f"Type:{aDriver.Type} Driver:{aDriver.ID}")

        self.name = self.GetName(aLabel)
        self.fullPath = self.GetFullPath(aLabel) 
        self.TFunctionID = self.GetDriverID()

        aDriver:Sym_Driver = self.GetDriver(self.TFunctionID)
        self.type = aDriver.type
        aDriver.Init(aLabel)
        self.params = aDriver.GetArgumentValue()
        return 

    @staticmethod
    def GetFullPath(theLabel:TDF_Label):
        stk_label = list()
        aLabel = theLabel
        stk_label.append(stk_label)
        fullPath = ""
        while not aLabel.IsRoot():
            aLabel = aLabel.Father()
            stk_label.append(aLabel)

        rootLabel = stk_label.pop()
        fullPath += rootLabel.GetLabelName()
        while len(stk_label) != 0:
            aLabel = stk_label.pop()
            fullPath += ":" + aLabel.GetLabelName()
        return fullPath

    @staticmethod
    def GetDriverID(theLabel:TDF_Label):
        aFunction:TFunction_Function = TFunction_Function()
        if not theLabel.FindAttribute(TFunction_Function.GetID(), aFunction):
            Logger().info("Object cannot be modified.")
            return
        return aFunction.GetDriverGUID()

    @staticmethod
    def GetName(theLabel: object):
        name = theLabel.GetLabelName()
        if len(name) <= 0:
            Logger().info("not a named object.")
            raise Exception("not a named object.")

        return name

    @staticmethod
    def GetDriver(guid):
        aDriver = Sym_Driver()
        TFunction_DriverTable.Get().FindDriver(guid, aDriver)
        return aDriver

    @staticmethod
    def GetParamValue(theDriver:Sym_Driver, ):
        dict_param = dict()
