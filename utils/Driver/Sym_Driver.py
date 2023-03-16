from utils.OCCUtils import (
    TFunction_DriverTable,
    TFunction_Logbook,
    TFunction_Function,
    TDF_Label,
    TDF_LabelList,
    TDF_Tool,
    TDataStd_TreeNode,
    TCollection_AsciiString,
    TDF_Attribute,
    FromText,
    TDataStd_Integer,
    
)
from typing import Union
from utils.GUID import *
from utils.Sym_Attribute import Sym_ShapeRef
from utils.decorator import classproperty
from utils.logger import Logger
"""
to have only one instance of a driver for the whole session.
"""


def GetDriver(obj:Union[Standard_GUID, TDF_Label]):
    aDriver = Sym_Driver()
    if isinstance(obj, Standard_GUID):
        id = obj
        TFunction_DriverTable.Get().FindDriver(id, aDriver)
    elif isinstance(obj, TDF_Label):
        aLabel = obj
        id = TFunction_Function.Set(aLabel).GetDriverGUID()
        TFunction_DriverTable.Get().FindDriver(id, aDriver)        

    return aDriver

class TagResource(object):
    def __init__(self) -> None:
        self.tag = 0

    def GetNewTag(self):
        self.tag += 1
        return self.tag

class Param(object):
    def __init__(self, theType:type, default:str="") -> None:
        self.type = theType
        self.default = default

    @property
    def Type(self):
        return self.type

    @property
    def Default(self):
        return self.default

    def __str__(self) -> str:
        return "{}".format(self.type)

    def __repr__(self) -> str:
        return self.__str__()

class Argument(object):
    def __init__(self, tag:TagResource, id:Standard_GUID, 
                 editFlag:bool=True) -> None:
        self._tag = tag.GetNewTag()
        self._driverID = id
        self._editFlag = editFlag

    @property
    def Tag(self):
        return self._tag

    @property
    def DriverID(self):
        return self._driverID

    def IsEdit(self):
        return self._editFlag

    def Value(self, fatheLabel:TDF_Label)->any:
        aDriver = GetDriver(self.DriverID)
        aLabel = fatheLabel.FindChild(self.Tag)
        return aDriver.GetValue(aLabel)

class Sym_Driver(object):
    """

    废弃复杂继承, 以组件形式组织数据
    """
    def __init__(self) -> None:
        # 函数定义
        self.Results:dict[str, dict] = dict()   # 结果
        self.Attributes:dict[str, dict] = dict()# 属性
        self.Arguments:dict[str, Argument] = dict() # 参数列表
        self.tagResource = TagResource()
        return

    def _base_init(self, L: TDF_Label)->bool:
        """ 函数初始化
        """
        def IsInit(theLabel:TDF_Label):
            aFunc = TFunction_Function()
            return theLabel.FindAttribute(aFunc.GetID(), aFunc)

        def _InitFunction(theLabel:TDF_Label):
            aLogBook = TFunction_Logbook.Set(theLabel)
            aFunction = TFunction_Function.Set(theLabel, self.ID)

        if IsInit(L): 
            return True

        _InitFunction(L)
        return False

    def Init(self, L: TDF_Label) -> bool:
        if self._base_init(L):
            return True

        for argu in self.Arguments.values():
            argu:Argument
            aLabel = L.FindChild(argu.Tag)
            aDriver:Sym_Driver = GetDriver(argu.DriverID)
            aDriver.Init(aLabel)

        return False

    def MustExecute(self, theLabel:TDF_Label, log: TFunction_Logbook) -> bool:
        """
        # !我们调用此方法来检查对象是否已被修改为要调用。
        # !如果修改了对象标签或参数，我们必须重新计算对象 - 调用方法 Execute（）。
        """
        if log.IsModified(theLabel):
            return True

        return False

    def GetStoredValue(self, theLabel:TDF_Label):
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)

        atype = self.Attributes['value'].Type
        container = atype()
        if not theLabel.FindAttribute(atype.GetID(), container):
            Logger().warn(f'Entry:{aEntry}{atype} get value error')
            return None

        value = container.Get()
        if value is None:
            Logger().warn(f'Entry:{aEntry}({atype}) get value None')            
            return None
 
        Logger().info(f'Entry:{aEntry} get value {str(value)} ')
        return value

    def GetValue(self, theLabel:TDF_Label):
        return self.GetStoredValue(theLabel)

    def _Log_ChangeValue(self, theLabel:TDF_Label, text):
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f"Label:{aEntry}({self.Type}) set value = {text}")

    def ChangeValue(self, theLabel:TDF_Label, text):
        self._Log_ChangeValue(theLabel, text)
        aType = self.Attributes['value'].Type
        value = aType.Set(theLabel, FromText(aType, text))
        Logger().info(f"stored value is {value.Get()}")

        return 

    def Validate(self, log: TFunction_Logbook) -> None:
        """ 验证对象标签、其参数和结果。"""
        log.SetValid(self.Label(), False)

    def Update(self, theLabel:TDF_Label, log: TFunction_Logbook) -> bool:
        if self.MustExecute(theLabel, log):
            self.Execute(theLabel, log)
            self.BroadcastImpacted(theLabel, log)
            return True

        return False

    def BroadcastImpacted(self, theLabel: TDF_Label, log: TFunction_Logbook):
        log.setUnTouched(theLabel)
        log.setUnImpacted(theLabel)
        aEntry = TCollection_AsciiString()

        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f'Entry:{aEntry} broadcast updated')
        father = theLabel.Father()
        log.SetTouched(father)

        TDF_Tool.Entry(father, aEntry)
        Logger().info(f'Entry:{aEntry} be impacted')


        TN = Sym_ShapeRef()
        if theLabel.FindAttribute(Sym_ShapeRef.GetID, TN):
            for node in TN:
                log.SetTouched(TN)

                TDF_Tool.Entry(node, aEntry)
                Logger().info(f'Entry:{aEntry} be impacted')

    def Execute(self, theLabel:TDF_Label, log: TFunction_Logbook) -> int:
        """ 执行函数, 根据参数.

        Args:
            theLabel (TDF_Label): _description_
            log (TFunction_Logbook): _description_

        Returns:
            bool: _description_
        """
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f'Entry:{aEntry} type:{self.Type} Execute')
        return 0

    def GetArguments(self, aLabel:TDF_Label, args: TDF_LabelList) -> None:
        return None

    def GetResults(self, aLabel:TDF_Label, args: TDF_LabelList) -> None:
        return None

    @classproperty
    def ID():
        """函数ID

        Raises:
            Exception: _description_
        """
        raise Exception("Must have ID")

    @classproperty
    def Type():
        """ 函数名
        """
        raise Exception("Must have Name")

class Sym_ShapeRefDriver(Sym_Driver):
    def __init__(self) -> None:
        super().__init__()
        self.myAttr = Param(Sym_ShapeRef)
        self.Attributes['value'] = self.myAttr

    def Init(self, L: TDF_Label) -> bool:
        if super().Init(L):
            return True

        Sym_ShapeRef.Set(L)
        return False

    def ChangeValue(self, theLabel:TDF_Label, text:str):
        self._Log_ChangeValue(theLabel, text)
        anEntry = TCollection_AsciiString(text)
        refedLabel = TDF_Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, refedLabel)
        Sym_ShapeRef.Set(theLabel, refedLabel)

        return True

    def GetValue(self, theLabel: TDF_Label) -> any:

        storedValue:TDF_Label = self.GetStoredValue(theLabel)
        if storedValue:
            aDriver = GetDriver(storedValue)
            value = aDriver.GetValue(storedValue)

            return value

        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().warn(f"Entry:{aEntry} not found reference")
        return None

    def Execute(self, theLabel: TDF_Label, log: TFunction_Logbook) -> int:
        return super().Execute(theLabel, log)

    @classproperty
    def Type(self):
        return "ShapeRef"

    @classproperty
    def ID(self):
        return Sym_ShapeRefDriver_GUID
