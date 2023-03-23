
from typing import Union

from OCC.Core.TDF import TDF_Tool

from RedPanda.RDAF.GUID import *

from RedPanda.decorator import classproperty
from RedPanda.logger import Logger

from RedPanda.Core.data import (
    RP_GUID,
    RP_AsciiStr
)
from ..RD_Label import Label
from ..Attribute import (
    FromText,
    TFunction_Function,
    Attr_ShapeRef,
    Attr_Guid,
    TDataStd_Integer,
)
from ..DriverTable import DataDriverTable
from ..Attribute import Lookup_Attr
"""
to have only one instance of a driver for the whole session.
"""

class TagResource(object):
    def __init__(self) -> None:
        self.tag = 0

    def GetNewTag(self):
        self.tag += 1
        return self.tag

class Param(object):
    """参数对象

    Args:
        object (_type_): _description_
    """
    def __init__(self, theAttrID:RP_GUID, value:str="", editAble=True) -> None:
        self.id = theAttrID
        self.edit = editAble
        if isinstance(value, str):
            self.value = value
        else:
            self.value = str(value)

    @property
    def Type(self):
        return self.type

    def SetValue(self, theLabel:Label, text:str):
        Lookup_Attr[self.id].Set(theLabel, FromText(self.Type, text))

    def GetValue(self, theLabel:Label):
        value = theLabel.GetAttrValue(self.id)
        if value is None:
            Logger().warn(f'Entry:{theLabel.GetEntry()}() get attr {self.id} None')
            return None

        return value
        

    def __str__(self) -> str:
        return f"{Lookup_Attr[self.id]}"

    def __repr__(self) -> str:
        return self.__str__()

class Argument(object):
    """属性对象

    Args:
        object (_type_): _description_
    """
    def __init__(self, tag:TagResource, id:RP_GUID, 
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


    def Value(self, theLabel:Label)->any:
        aDriver = DataDriverTable(self.DriverID)
        aLabel = theLabel.FindChild(self.Tag)
        return aDriver.GetValue(aLabel)

class DataDriver(object):
    """
        Base Execute Driver
    """
    def __init__(self) -> None:
        self.tagResource = TagResource()
        self.Results: dict[str, dict] = dict()          # 结果
        self.Attributes: dict[str, RP_GUID] = dict()    # 属性
        self.Arguments: dict[str, Argument] = dict()    # 参数

    def myInit(self, theLabel:Label, theData):
        raise NotImplementedError()

    def myChange(self, theLabel:Label, theData):
        raise NotImplementedError()

    def Init(self, theLabel:Label, theData):
        self._base_init()
        self.myInit(theLabel, theData)
        if self.Execute(theLabel) != 0:
            return False

    def GetValue(self, theLabel:Label):
        raise NotImplementedError()

    def GetValueToText(self, theLabel:Label):
        return str(self.GetValue(theLabel))

    def Change(self, theLabel:Label, theData):
        self.myChange(theLabel, theData)

    def Execute(self, theLabel:Label)->int:
        return 0

    def GetRefMeLabel(self, theLabel)->set[Label]:
        label_set = set()
        if not theLabel.IsRoot():
            father = theLabel.Father()
            label_set.add(father)

        shape_Ref = Attr_ShapeRef()
        if theLabel.FindAttribute(Attr_ShapeRef.GetID(), shape_Ref):
            for node in shape_Ref:
                label_set.add(node)

        return label_set

    def _base_init(self, theLabel: Label):
        Logger().info(f'create Label:{theLabel.GetEntry()}, {None}, {self.ID}')
        TFunction_Function.set(theLabel, self.ID)


    @classproperty
    def ID(self):
        """函数ID

        Raises:
            Exception: _description_
        """
        raise NotImplementedError('Must have ID')

    @classproperty
    def Type(self):
        """ 函数名
        """
        raise NotImplementedError('Must have Type')

class VarDriver(DataDriver):
    def myInit(self, theLabel: Label, theData):
        Logger().info(f'change Label:{theLabel.GetEntry()}.value, {None}, {theData}')
        attr:Param = self.Attributes['value']
        attr.SetValue(theLabel, theData)

    def myChange(self, theLabel: Label, theData):
        attr:Param = self.Attributes['value']
        Logger().info(f'change var:{theLabel.GetEntry()}.value, ' +
                      f'{attr.GetValue(theLabel)}, {theData}')

        attr.SetValue(theLabel, theData)

    def GetValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

class ShapeRefDriver(DataDriver):
    def __init__(self) -> None:
        super().__init__()
        self.Attribute['ref'] = Param(Attr_ShapeRef)

    def myInit(self, theLabel: Label, text):
        anEntry = RP_AsciiStr(text)
        aRefLabel = Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, aRefLabel)
        Attr_ShapeRef.Set(theLabel, aRefLabel)

    def myChange(self, theLabel:Label, theData):
        return 0

    def GetValue(self, theLabel: Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            aDriver = reflabel.GetDriver()
            value = aDriver.GetValue(reflabel)
            return value

        Logger().warn(f'Entry:{theLabel.GetEntry()} not found reference')
        return None

class ArrayDriver(DataDriver):
    def __init__(self, ) -> None:
        super().__init__()
        self.myAttr = Param(TDataStd_Integer)
        self.Attributes['size'] = self.myAttr
        # self.Attributes['type'] = Param(Attr_Guid)

        self._ArrayFirstTag = 125
        self._SubTypeId = Sym_PntDriver_GUID
        # self._ID = driverID

    @property
    def StartIndex(self):
        return self._ArrayFirstTag

    def GetSize(self, theLabel: Label):
        aInt = theLabel.GetAttrValue(self.Attributes['type'].id)
        return aInt

    def myInit(self, theLabel:Label, theData:dict):
        TDataStd_Integer.Set(theLabel, len(theData))
        aDriver = theLabel.GetDriver()
        for ind, pnt in enumerate(theData.values()):
            tag = ind+self._ArrayFirstTag
            aLabel = theLabel.FindChild(tag)
            aDriver.Init(aLabel, pnt)

    def myChange(self, theLabel:Label, theData:dict):
        aDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)
        for ind, pnt in theData.items():
            tag = int(ind)+self.StartIndex
            aLabel = theLabel.FindChild(tag, False)
            aDriver.Change(aLabel, pnt)
        return True


class ShapeDriver(DataDriver):
    def myInit(self, theLabel: Label, theData):
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver = DataDriverTable.Get().GetDriver(argu.DriverID)
            aDriver.Init(aLabel, theData[name])
        if self.Execute(theLabel) != 0:
            return False
        return True

    def myChange(self, theLabel: Label, theData):
        for name, subData in theData.items():
            argu:Argument = self.Arguments[name]
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:DataDriver = DataDriverTable.Get().GetDriver(argu.DriverID)
            if not aDriver.Change(aLabel, subData):
                return False
        if self.Execute(theLabel) != 0:
            return False
        return True

    def GetValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

'''
class DataDriver(object):
    """ Shape Driver

    """
    def __init__(self) -> None:
        # 函数定义
        self.Results:dict[str, dict] = dict()   # 结果
        self.Attributes:dict[str, Param] = dict()# 属性
        self.Arguments:dict[str, Argument] = dict() # 参数列表
        self.tagResource = TagResource()
        return

    def _base_init(self, L: Label)->bool:
        """ 函数初始化
        """
        def IsInit(theLabel:Label):
            aFunc = TFunction_Function()
            return theLabel.FindAttribute(aFunc.GetID(), aFunc)

        def _InitFunction(theLabel:Label):
            aLogBook = TFunction_Logbook.Set(theLabel)
            aFunction = TFunction_Function.Set(theLabel, self.ID)
            anEntry = GetEntry(theLabel)
            Logger().info(f'Entry:{anEntry} init with driver:{self.ID}')

        if IsInit(L): 
            return True

        _InitFunction(L)
        return False

    def InitValue(self, theLabel, theData:str):
        attr = self.Attributes['value']
        attr.SetValue(theLabel, theData)

    def Init(self, L: Label, theData:Union[dict,str]) -> bool:
        if self._base_init(L):
            return True

        if isinstance(theData, dict): # dict 向下传播
            Logger().info(f'{self.Type} init sub')
            for name, argu in self.Arguments.items():
                argu:Argument
                aLabel = L.FindChild(argu.Tag)
                aDriver:Sym_Driver = GetDriver(argu.DriverID)
                if not aDriver.Init(aLabel, theData[name]):
                    return False
        else:
            Logger().info(f'{self.Type} init self')
            self.InitValue(L, theData)

        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(L, aEntry)
        Logger().info('Entry:{aEntry} init sub success')
        if self.Execute(L) != 0:
            return False
        return True

    def Execute(self, theLabel:Label) -> int:
        """ 执行函数, 根据参数.

        Args:
            theLabel (Label): _description_
            log (TFunction_Logbook): _description_

        Returns:
            bool: _description_
        """
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f'Entry:{aEntry} type:{self.Type} Execute')
        return 0

    def MustExecute(self, theLabel:Label, log: TFunction_Logbook) -> bool:
        """
        # !我们调用此方法来检查对象是否已被修改为要调用。
        # !如果修改了对象标签或参数，我们必须重新计算对象 - 调用方法 Execute。
        """

        raise Exception('abolished')
        
        if log.IsModified(theLabel):
            return True

        return False

    def GetStoredValue(self, theLabel:Label):
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

    def GetValue(self, theLabel:Label):
        storedvalue = self.GetStoredValue(theLabel)
        return storedvalue

    def GetValueToText(self, theLabel:Label):
        return str(self.GetValue(theLabel))

    def _Log_ChangeValue(self, theLabel:Label, text):
        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f"Label:{aEntry}({self.Type}) set value = {text}")

    def ChangeValue(self, theLabel:Label, theData:str):
        self._Log_ChangeValue(theLabel, theData)
        attr = self.Attributes['value']
        attr.SetValue(theLabel, theData)

    def Change(self, theLabel:Label, theData:Union[dict, str]):
        if isinstance(theData, dict): # dict 向下传播
            for name, subData in theData.items():
                argu:Argument = self.Arguments[name]
                aLabel = theLabel.FindChild(argu.Tag)
                aDriver:Sym_Driver = GetDriver(argu.DriverID)
                if not aDriver.Change(aLabel, subData):
                    return False
        else:
            Logger().info(f'{self.Type} change self')
            self.ChangeValue(theLabel, theData)

        aEntry = TCollection_AsciiString()
        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info('Entry:{aEntry} Change sub success')
        if self.Execute(theLabel) != 0:
            return False
        return True

    def Validate(self, log: TFunction_Logbook) -> None:
        """ 验证对象标签、其参数和结果。"""
        log.SetValid(self.Label(), False)

    def Update(self, theLabel:Label, log:TFunction_Logbook) -> bool:
        raise Exception("abolished")
        if self.MustExecute(theLabel, log):
            self.Execute(theLabel)
            self.BroadcastImpacted(theLabel, log)
            return True

        return False

    @staticmethod
    def BroadcastImpacted(theLabel:Label):
        label_set:set[Label] = set()
        aEntry = TCollection_AsciiString()

        TDF_Tool.Entry(theLabel, aEntry)
        Logger().info(f'Entry:{aEntry} broadcast updated')

        if not theLabel.IsRoot():
            father = theLabel.Father()
            TDF_Tool.Entry(father, aEntry)
            Logger().info(f'Entry:{aEntry} be impacted')
            label_set.add(father)

        TN = Sym_ShapeRef()
        if theLabel.FindAttribute(Sym_ShapeRef.GetID(), TN):
            Logger().debug('Find chidren.')
            for node in TN:
                TDF_Tool.Entry(node, aEntry)
                Logger().info(f'Entry:{aEntry} be impacted')
                label_set.add(node)

        return label_set

    def GetArguments(self, aLabel:Label, args:LabelList) -> None:
        return None

    def GetResults(self, aLabel:Label, args:LabelList) -> None:
        return None

    @classproperty
    def ID(self):
        """函数ID

        Raises:
            Exception: _description_
        """
        raise Exception("Must have ID")

    @classproperty
    def Type(self):
        """ 函数名
        """
        raise Exception("Must have Name")
'''