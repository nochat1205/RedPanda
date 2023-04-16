from __future__ import annotations

from typing import Union

from OCC.Core.TPrsStd import TPrsStd_Driver
from OCC.Core.AIS import AIS_InteractiveObject
from OCC.Core.TDF import TDF_Tool

from RedPanda.decorator import classproperty
from RedPanda.logger import Logger

from RedPanda.RPAF.GUID import *
from RedPanda.RPAF.RD_Label import Label
from RedPanda.Core.data import (
    RP_GUID,
    RP_AsciiStr,
)
from .InArgu import 实参
from ..RD_Label import Label
from ..Attribute import (
    FromText,
    TFunction_Function,
    Attr_ShapeRef,
    Attr_Guid,
    Attr_Entry,
    TDataStd_Integer,
    Attr_State
)
from ..Attribute import Lookup_Attr

"""
to have only one instance of a driver for the whole session.
"""

class DataEnum:
    Null = 0
    Real = 1
    Int = 2
    PntArray = 5


    Shape = 10
    Vertex = 13
    Edge = 14
    Wire = 15
    Face = 16
    Shell = 17
    Solid = 18
    @staticmethod
    def IsShape(enum):
        return 10 <= enum and enum <= 20 

class DataLabelState:
    """
    状态标志, 表示DataLabel 数据是否可访问.
    """
    OK = 0
    ParamError = 1
    @staticmethod
    def Init(theLabel:Label):
        DataLabelState.SetError(theLabel)

    @staticmethod
    def _SetState(theLabel:Label, state:DataLabelState):
        Attr_State.Set(theLabel, state)

    @staticmethod
    def SetOK(theLabel:Label):
        Attr_State.Set(theLabel, DataLabelState.OK)

    @staticmethod
    def SetError(theLabel:Label):
        Attr_State.Set(theLabel, DataLabelState.ParamError)

    @staticmethod
    def IsOK(theLabel:Label):
        value = theLabel.GetAttrValue(Attr_State.GetID())
        if value:
            value = DataLabelState.OK
            return True
        return False

class TagResource(object):
    def __init__(self) -> None:
        self.tag = 0

    def GetNewTag(self):
        self.tag += 1
        return self.tag

class Param(object):
    """ 属性对象声明
    """
    def __init__(self, theAttrID:RP_GUID, value:str="", editAble=True) -> None:
        assert isinstance(theAttrID, RP_GUID)

        self.id = theAttrID
        self.edit = editAble
        if isinstance(value, str):
            self.value = value
        else:
            self.value = str(value)

    @property
    def Type(self):
        return Lookup_Attr[self.id]

    def SetValue(self, theLabel:Label, text:str):
        Lookup_Attr[self.id].Set(theLabel, FromText(self.Type, text))

    def GetAttribute(self, theLabel:Label):
        return theLabel.GetAttribute(self.id)

    def GetValue(self, theLabel:Label):
        return theLabel.GetAttrValue(self.id)

    def __str__(self) -> str:
        return f"{Lookup_Attr[self.id]}"

    def __repr__(self) -> str:
        return self.__str__()

class Argument(object):
    """ 子label 声明
    """
    def __init__(self, tag:TagResource, id:RP_GUID, 
                 editFlag:bool=True, valueType:int = DataEnum.Null) -> None:
        self._tag = tag.GetNewTag()
        self._driverID = id
        self._editFlag = editFlag
        self.valueType = valueType

    @property
    def Tag(self):
        return self._tag

    @property
    def DriverID(self):
        return self._driverID

    def IsEdit(self):
        return self._editFlag

    def Value(self, theLabel:Label)->any:
        from ..DriverTable import DataDriverTable

        aDriver = DataDriverTable.Get().GetDriver(self.DriverID)
        aLabel = theLabel.FindChild(self.Tag)
        return aDriver.GetValue(aLabel)


class DataDriver(object):
    """ base and manager
        通过函数接口访问数据, 方便更新.
    """
    OutputType = DataEnum.Null

    def __init__(self) -> None:
        self.name:str = ''
        self.id:RP_GUID = None

        self.description:str = ''
        self.long_description:str = ''

        self.socket_0tag = 64

        # old        
        self.tagResource = TagResource()
        self.Results: dict[str, dict] = dict()          # 结果
        self.Attributes: dict[str, RP_GUID] = dict()    # 属性
        self.Arguments: dict[str, Argument] = dict()    # 参数

        # New
        self.input_params = self.Arguments

    def myInit(self, theLabel:Label, theData: 实参)->bool:
        ''' 运行自己的参数检查和初始化就行
        返回初始化是否成功 <= 参数是否正确
        '''
        raise NotImplementedError()

    def myChange(self, theLabel:Label, theData:实参):
        # 只管更改
        raise NotImplementedError()

    def myTextValue(self, theLabel:Label):
        ''' 只复制取出值的text形式
        '''
        return str(self.myValue(theLabel))

    def myValue(self, theLabel:Label):
        ''' 只复制取出DataLabel 的value值
        '''
        raise NotImplementedError()

    def myExecute(self, theLabel:Label)->int:
        """ 仅负责获取参数和执行
        """
        return 0

    def Init(self, theLabel:Label, theData):
        """ 执行函数 - 初始化
        必要的初始化, 根据实话结果设置状态
        """
        self._base_init(theLabel)
        if not self.myInit(theLabel, theData):
            DataLabelState.SetError(theLabel)
            return False

        if not self.Execute(theLabel):
            DataLabelState.SetError(theLabel)
            return False

        DataLabelState.SetOK(theLabel)
        return True

    def GetArguLabel(self, theLabel:Label)->list[Label]:
        label_li = list()
        for argu in self.Arguments.values():
            argu:Argument
            sub = theLabel.FindChild(argu.Tag, False)
            label_li.append(sub)

        return label_li

    def Update(self, L: Label, ais: AIS_InteractiveObject) -> bool:
        """ for TPrsStd_AISPrsentaion, 
        由于ocaf TPrsStd_AISPrsentaion的原因,只能命名为Update
        """
        raise NotImplementedError()

    def GetValue(self, theLabel:Label):
        if not DataLabelState.IsOK(theLabel):
            return None
        
        return self.myValue()
    
    def GetTextValue(self, theLabel:Label):
        if not DataLabelState.IsOK(theLabel):
            return 'Label is error'
        return self.myTextValue(self.myTextValue)

    def Change(self, theLabel:Label, theData):
        """ 管理函数 更改
        """

        if not self.myChange(theLabel, theData):
            DataLabelState.SetError(theLabel)
            return False

        if not self.Execute(theLabel):
            DataLabelState.SetError(theLabel)
            return False
        DataLabelState.SetOK(theLabel)
        return True

    def Execute(self, theLabel:Label)->bool:
        """ 管理函数 - 执行
        """
        subLabel_li = self.GetArguLabel(theLabel)
        for sub in subLabel_li:
            if not DataLabelState.IsOK(sub):
                return False

        if self.myExecute(theLabel) != 0:
            return False
        
        return True

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
        TFunction_Function.Set(theLabel, self.ID)
        DataLabelState.Init(theLabel)

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

class SocketDriver(object):
    def __init__(self) -> None:
        self.__socketType = ''

from ..DriverTable import DataDriverTable
class VarDriver(DataDriver):
    def myInit(self, theLabel: Label, theData='0'):
        Logger().info(f'change Label:{theLabel.GetEntry()}.value, {None}, {theData}')
        attr:Param = self.Attributes['value']
        attr.SetValue(theLabel, theData)
        return True

    def myChange(self, theLabel: Label, theData):
        attr:Param = self.Attributes['value']
        Logger().info(f'change var:{theLabel.GetEntry()}.value, ' +
                      f'{attr.GetValue(theLabel)}, {theData}')

        attr.SetValue(theLabel, theData)
        return True

    def myValue(self, theLabel: Label):

        return self.Attributes['value'].GetValue(theLabel)

class ShapeRefDriver(DataDriver):
    OutputType = DataEnum.Shape

    def __init__(self) -> None:
        super().__init__()
        self.Attributes['ref'] = Param(Attr_ShapeRef.GetID())
        # self.Attributes['value'] = Param(Attr_Entry.GetID())

    def myInit(self, theLabel: Label, text='0')->bool:
        if text == '0':
            Attr_ShapeRef.Set(theLabel)
            return False

        anEntry = RP_AsciiStr(text)
        aRefLabel = Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, aRefLabel)
        Attr_ShapeRef.Set(theLabel, aRefLabel)
        return True

    def myChange(self, theLabel:Label, theData):
        shapeRef_attr:Attr_ShapeRef = self.Attributes['ref'].GetAttribute(theLabel)
        if shapeRef_attr:
            shapeRef_attr.Remove()

        anEntry = RP_AsciiStr(theData)
        aRefLabel = Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, aRefLabel)
        if aRefLabel.IsNull():
            return False

        Attr_ShapeRef.Set(theLabel, aRefLabel)
        return True

    def myValue(self, theLabel: Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            aDriver = reflabel.GetDriver()
            value = aDriver.GetValue(reflabel)
            return value

        Logger().warn(f'Entry:{theLabel.GetEntry()} not found reference')
        return None

    def myValueToText(self, theLabel: Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            return str(reflabel)

        Logger().warn(f'Entry:{theLabel.GetEntry()} not found reference')
        return 'Null'

    @classproperty
    def ID(self):
        """函数ID

        Raises:
            Exception: _description_
        """
        return ShapeRefGUID

    @classproperty
    def Type(self):
        """ 函数名
        """
        return 'ShapeRef'

class ArrayDriver(DataDriver):
    OutputType = DataEnum.PntArray
    def __init__(self, ) -> None:
        super().__init__()
        

        self.myAttr = Param(TDataStd_Integer.GetID())
        self.Attributes['size'] = self.myAttr

        self._ArrayFirstTag = 125
        self._SubTypeId = Sym_PntDriver_GUID
        # self._ID = driverID

    @property
    def StartIndex(self):
        return self._ArrayFirstTag

    def GetSize(self, theLabel: Label):
        aInt = theLabel.GetAttrValue(self.Attributes['type'].id)
        return aInt

    def myInit(self, theLabel:Label, size=0):
        TDataStd_Integer.Set(theLabel, size)
        # aDriver = theLabel.GetDriver()
        # for ind, pnt in enumerate(theData.values()):
        #     tag = ind+self._ArrayFirstTag
        #     aLabel = theLabel.FindChild(tag)
        #     aDriver.Init(aLabel, pnt)

    def myChange(self, theLabel:Label, size):

        # aDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)

        # for ind, pnt in theData.items():
        #     tag = int(ind)+self.StartIndex
        #     aLabel = theLabel.FindChild(tag, False)
        #     if not aDriver.Change(aLabel, pnt):
        #         return False
        # return True
        start = self.StartIndex()
        oldsize = self.GetSize()
        if size > oldsize:
            for ind in range(oldsize, size):
                sub = theLabel.FindChild(start+ind)
        TDataStd_Integer.Set(theLabel, size)
        return True

    def GetArguLabel(self, theLabel: Label) -> list[Label]:
        sublabel_li = list()
        size = self.GetSize(theLabel)
        start = self.StartIndex()
        for ind in range(size, size+start):
            sublabel_li.append(theLabel.FindChild(ind))

        return sublabel_li
