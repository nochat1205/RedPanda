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
from utils.logger import Logger

class Sym_NewBuilder(object):
    """_summary_

    Args:
        param (dict): {"type":, "default":value}
    """
    def __init__(self, aDriver:Sym_Driver, parent=None) -> None:
        self.type = aDriver.Type
        self.parent = parent
        self.TFunctionID = aDriver.ID
        Logger().debug("ID:"+str(self.TFunctionID))
        self.params:dict = self.GetParamDefination(aDriver)
        Logger().debug("ID:"+str(self.TFunctionID))

    @staticmethod
    def GetParamDefination(aDriver:Sym_Driver):
        """
        Args:
            aDriver (Sym_Driver): _description_
        """
        def GetParamWith(aDriver: Sym_Driver):
            dict_param = {}
            # load attri
            Attri = aDriver.Attributes
            Logger().debug("TypeF:"+str(type(aDriver))+":"+aDriver.Type)
            Logger().debug('Type:'+aDriver.Type+":"+str("value" in Attri))
            if "value" in Attri:
                dict_param["value"] = Attri["value"]

            # load children
            dict_child = dict()
            for name, param in aDriver.Arguments.items():
                param:Argument
                Logger().debug("nameA:"+name)
                children = GetParamWith(GetDriver(param.DriverID))
                dict_child[name] = children
            if len(dict_child) > 0:
                dict_param["children"] = dict_child
            return dict_param

        dict_param = dict()
        dict_param["Name"] = Param(str, "debug")
        dict_param['Parent'] = Param(str, "main")
        dict_param['Shape'] = GetParamWith(aDriver)

        return dict_param

class Sym_ChangeBuilder(object):
    def __init__(self, aLabel: TDF_Label):
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
