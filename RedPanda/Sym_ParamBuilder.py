from RedPanda.logger import Logger
from RedPanda.RPAF.GUID import *
from RedPanda.RPAF.RD_Label import  Label
from RedPanda.RPAF.DataDriver import (
    DataDriver,
    Argument
)
from  RedPanda.RPAF.DriverTable import DataDriverTable

def _GetDriver(id):
    aDriver = DataDriverTable.Get().GetDriver(id)
    return aDriver

class NodeParam(object):
    """参数对象
    Args:
        object (_type_): _description_
    """
    def __init__(self, value:str="", editAble=True) -> None:
        self.edit = editAble
        if isinstance(value, str):
            self.value = value
        else:
            self.value = str(value)

    @property
    def Type(self):
        return self.type

    def __str__(self) -> str:
        return f"{self.value}"

    def __repr__(self) -> str:
        return self.__str__()

class ArrayParam(object):
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
    
    def __init__(self, aDriver:DataDriver, parent=None) -> None:
        Logger().info('Start init NewParamBuilder ')
        Logger().info(f"Type:{aDriver.Type} Driver:{aDriver.ID}")

        self.type = aDriver.Type
        self.TFunctionID = aDriver.ID
        self.name_param = NodeParam("shape")
        self.parent_param = NodeParam("0:1")

        self.shape_param:dict = self.GetDefination(aDriver)
        Logger().info(f'name:{self.name_param}')
        Logger().info(f'parent:{self.parent_param}')
        Logger().info(f'shape:{self.shape_param}')
        Logger().info('End init NewParamBuilder ')

    @staticmethod
    def GetParamWith(aDriver: DataDriver):
        def GetParamDefault(aDriver:DataDriver):
            if len(aDriver.Arguments) > 0: # read children
                child_ParamDict = {}
                for name, param in aDriver.Arguments.items():
                    param:Argument
                    child_param = Sym_NewBuilder.GetParamWith(
                            _GetDriver(param.DriverID)
                        )
                    child_ParamDict[name] = child_param
                return child_ParamDict
            else: # read leave value
                Attri = NodeParam(aDriver.Attributes['value'].value)
                return Attri

        def GetArrayParam(aDriver:DataDriver):
            subDriver = _GetDriver(aDriver._SubTypeId)
            return ArrayParam(GetParamDefault(subDriver))

        param = None
        assert isinstance(aDriver, DataDriver)
        if aDriver.ID == Sym_ArrayDriver_GUID:
            param = GetArrayParam(aDriver)
        else:
            param = GetParamDefault(aDriver)
        return param

    @staticmethod
    def GetDefination(aDriver:DataDriver):
        return Sym_NewBuilder.GetParamWith(aDriver)

class Sym_ChangeBuilder(object):
    def __init__(self, theLabel: Label):
        Logger().info('Start init ChangeParamBuilder ')

        aDriver = theLabel.GetDriver()
        self.TFunctionID = theLabel.GetFunctionID()
        self.type = aDriver.Type
        self.name_param = NodeParam(theLabel.GetLabelName())
        self.parent_param = NodeParam(theLabel.GetEntry(), editAble=False)

        self.shape_param = self.GetObjectData(theLabel)
        Logger().info(f'params:{self.shape_param}')
        Logger().info('End init ChangeParamBuilder ')
        return 


    @staticmethod
    def GetParamWith(theLabel: Label):
        # Logger().debug(f)
        def GetSubObjectData(theLabel: Label):
            aDriver = theLabel.GetDriver()
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
                return NodeParam(aDriver.GetValueToText(theLabel))

        def GetArrayData(theLabel:Label):
            child_dict = {}
            aDriver = theLabel.GetDriver()
            start = aDriver.StartIndex
            size = aDriver.GetSize(theLabel)
            Logger().debug(f'GetArrayData size:{size}')
            for i in range(size):
                aLabel = theLabel.FindChild(i+start, False)
                child_dict[str(i)] = GetSubObjectData(aLabel)
            return child_dict

        aDriver = theLabel.GetDriver()
        Logger().info(f"Entry:{theLabel.GetEntry()} id:{aDriver.ID} Get Param")
        if aDriver.ID == Sym_ArrayDriver_GUID:
            data = GetArrayData(theLabel)
        else:
            data = GetSubObjectData(theLabel)
        return data

    @staticmethod
    def GetObjectData(theLabel:Label):
        return Sym_ChangeBuilder.GetParamWith(theLabel)

