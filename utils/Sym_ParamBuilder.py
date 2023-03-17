from OCC.Core.TDF import TDF_Label

from utils.OCCUtils import (
    TFunction_Function, 
    TFunction_DriverTable,
    Standard_GUID,
    TCollection_AsciiString,
    TDF_Tool
)
from utils.Driver.Sym_Driver import (
    Sym_Driver,
    Argument,
    GetDriver,
    GetEntry,
    GetFunctionID,
    Param,
    GetFunctionID
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
    def __init__(self, theLabel: TDF_Label):
        Logger().info('Start init ChangeParamBuilder ')

        self.TFunctionID = Sym_ChangeBuilder.GetDriverID(theLabel)
        aDriver = GetDriver(self.TFunctionID)

        self.type = aDriver.Type
        self.name_param = Param(str, self.GetName(theLabel))
        self.parent_param = Param(str, self.GetEntry(theLabel), editAble=False)

        self.shape_param = self.GetObjectData(theLabel)
        Logger().info(f'Entry:{GetEntry(theLabel)} name:{self.name_param.Default} type:{self.type}')
        Logger().info(f'params:{self.shape_param}')
        Logger().info('End init ChangeParamBuilder ')
        return 

    @staticmethod
    def GetEntry(theLabel:TDF_Label):
        return GetEntry(theLabel)

    @staticmethod
    def GetDriverID(theLabel:TDF_Label):
        return GetFunctionID(theLabel)

    @staticmethod
    def GetDriver(theLabel:TDF_Label):
        return GetDriver(theLabel)

    @staticmethod
    def GetName(theLabel: object):
        name = theLabel.GetLabelName()
        if len(name) <= 0:
            Logger().info("not a named object.")
            raise Exception("not a named object.")

        return name

    @staticmethod
    def GetParamWith(theLabel: TDF_Label):
        # Logger().debug(f)
        def GetSubObjectData(theLabel: TDF_Label):
            aDriver = GetDriver(theLabel)
            if len(aDriver.Arguments) > 0: # read children
                child_ParamDict = {}
                for name, argu in aDriver.Arguments.items():
                    argu:Argument
                    child_param = Sym_ChangeBuilder.GetParamWith(
                            theLabel.FindChild(argu.Tag, False)
                    )
                    child_ParamDict[name] = child_param
                return child_ParamDict
            else: # read leave value
                Attri:Param = aDriver.Attributes['value']

                return Param(Attri.Type, aDriver.GetValueToText(theLabel))

        def GetArrayData(theLabel:TDF_Label):
            child_dict = {}
            aDriver:Sym_ArrayDriver_GUID = GetDriver(theLabel)
            start = aDriver.StartIndex
            size = aDriver.GetSize(theLabel)
            Logger().debug(f'GetArrayData size:{size}')
            for i in range(size):
                aLabel = theLabel.FindChild(i+start, False)
                child_dict[str(i)] = GetSubObjectData(aLabel)
            return child_dict

        aDriver = Sym_ChangeBuilder.GetDriver(theLabel)
        Logger().info(f"Entry:{GetEntry(theLabel)} id:{aDriver.ID} Get Param")
        if aDriver.ID == Sym_ArrayDriver_GUID:
            data = GetArrayData(theLabel)
        else:
            data = GetSubObjectData(theLabel)
        return data

    @staticmethod
    def GetObjectData(theLabel:TDF_Label):
        return Sym_ChangeBuilder.GetParamWith(theLabel)

