from __future__ import annotations

from typing import Union

from OCC.Core.TPrsStd import TPrsStd_Driver
from OCC.Core.AIS import AIS_InteractiveObject
from OCC.Core.TDF import TDF_Tool
from OCC.Core.TNaming import TNaming_NamedShape, TNaming_Builder

from RedPanda.RPAF.DataDriver.InArgu import 实参

from RedPanda.decorator import classproperty
from RedPanda.logger import Logger

from RedPanda.RPAF.GUID import *
from RedPanda.RPAF.RD_Label import Label
from RedPanda.Core.data import (
    RP_GUID,
    RP_AsciiStr,
    RP_ExtendStr
)
from .InArgu import 实参
from ..RD_Label import Label
from ..Attribute import (
    FromText,
    TFunction_Function,
    Attr_ShapeRef,
    Attr_Guid,
    TDataStd_Integer,
    Attr_State,
    Attr_StateMessage,
    Attr_Exist

)
from ..Attribute import Lookup_Attr
# from ..Touched import TouchedLabel # ForArray

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
    状态标志, 表示DataLabel 数据是否可访问数据状态.
    """
    OK = 0
    ParamError = 1
    @staticmethod
    def Init(theLabel:Label):
        DataLabelState.SetOK(theLabel)

    @staticmethod
    def SetOK(theLabel:Label):
        Attr_StateMessage.Set(theLabel, RP_ExtendStr('Valid'))
        Attr_State.Set(theLabel, DataLabelState.OK)

    @staticmethod
    def SetError(theLabel:Label, ErrorMsg='NotValid', override=False):
        if override or DataLabelState.IsOK(theLabel):
            Attr_StateMessage.Set(theLabel, RP_ExtendStr(ErrorMsg))
            Attr_State.Set(theLabel, DataLabelState.ParamError)

    @staticmethod
    def GetMsg(theLabel:Label):
        return theLabel.GetAttrValue(Attr_StateMessage.GetID())

    @staticmethod
    def IsOK(theLabel:Label):
        value = theLabel.GetAttrValue(Attr_State.GetID())
        if value is not None:
            if value == DataLabelState.OK:
                return True
        return False

class Exist:
    '''
        标识节点是否存在
    '''
    @staticmethod
    def Init(theLabel:Label):
        return 
        Exist.SetExist(theLabel)

    @staticmethod
    def SetExist(theLabel:Label):
        return 
        Attr_Exist.Set(theLabel, 1)

    @staticmethod
    def SetDelete(theLabel:Label):
        return 
        Attr_Exist.Set(theLabel, 0)

    @staticmethod
    def IsExist(theLabel):
        return 
        value = theLabel.GetAttrValue(Attr_Exist.GetID())
        if value:
            return value > 0
        return False


class TagResource(object):
    def __init__(self) -> None:
        self.tag = 17

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
        try:
            Lookup_Attr[self.id].Set(theLabel, FromText(self.Type, text))
        except:
            return False
        return True

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

    def Label(self, theLabel:Label):
        return theLabel.FindChild(self.Tag, False)

    def Value(self, theLabel:Label, *args, **kwargs)->any:
        from ..DriverTable import DataDriverTable

        aLabel = theLabel.FindChild(self.Tag)
        aDriver = aLabel.GetDriver()
        return aDriver.GetValue(aLabel, *args, **kwargs)

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
        self.Attributes: dict[str, Param] = dict()      # 属性
        self.Arguments: dict[str, Argument] = dict()    # 参数

    def _base_init(self, theLabel: Label):
        Logger().info(f'BaseInit {theLabel.GetEntry()} {self.Type}')
        TFunction_Function.Set(theLabel, self.ID)
        DataLabelState.Init(theLabel)


    def myInit(self, theLabel:Label, data=None)->bool:
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
        raise Exception('Just 直接参数对象 have GetTextValue function')
        
    def myValue(self, theLabel:Label):
        ''' 只复制取出DataLabel 的value值
        '''
        raise NotImplementedError()

    def myExecute(self, theLabel:Label)->int:
        """ 仅负责获取参数和执行
        """
        return 0

    def Init(self, theLabel:Label, data=None):
        """ 执行函数 - 初始化
        必要的初始化, 根据实话结果设置状态
        """
        # if self._isInit(theLabel):
        #     Logger().info(f'Entry:{theLabel.GetEntry()}, had init')
        #     return True

        Logger().info(f'Entry:{theLabel.GetEntry()}, init start')

        self._base_init(theLabel)

        if not self.myInit(theLabel, data):
            DataLabelState.SetError(theLabel, 'Init Failed')
            Logger().warning(f'Entry:{theLabel.GetEntry()}, type:{self.Type}, Init Falied')

            return False

        if not self.Execute(theLabel):
            Logger().warning(f'Entry:{theLabel.GetEntry()}, type:{self.Type}, Execute Falied')
            DataLabelState.SetError(theLabel, 'Execute Falied')
            return False

        DataLabelState.SetOK(theLabel)
        Logger().info(f'Entry:{theLabel.GetEntry()}, init end')

        return True

    def GetArguLabel(self, theLabel:Label)->list[Label]:
        label_li = list()
        for argu in self.Arguments.values():
            argu:Argument
            sub = theLabel.FindChild(argu.Tag, False)
            label_li.append(sub)

        return label_li

    def GetNamedArgument(self, theLabel:Label)->dict[str, Label]:
        label_li = dict()
        for name, argu in self.Arguments.items():
            argu:Argument
            sub = theLabel.FindChild(argu.Tag, False)
            label_li[name] = sub
        return label_li

    def GetValue(self, theLabel:Label):
        if not DataLabelState.IsOK(theLabel):
            return None

        return self.myValue(theLabel)
    
    def GetTextValue(self, theLabel:Label):
        if not DataLabelState.IsOK(theLabel):
            return 'Label is error'
        return self.myTextValue(theLabel)

    def Change(self, theLabel:Label, theData):
        """ 管理函数 更改
        """
        if not self.myChange(theLabel, theData):
            DataLabelState.SetError(theLabel, 'ChangeError')
            return False

        if not self.Execute(theLabel):
            return False

        return True

    def Execute(self, theLabel:Label)->bool:
        """ 管理函数 - 执行
        """
        subLabel_li = self.GetArguLabel(theLabel)
        for sub in subLabel_li:
            if sub is None or not DataLabelState.IsOK(sub):
                DataLabelState.SetError(theLabel, 'Param Error')
                return False

        if self.myExecute(theLabel) != 0:
            DataLabelState.SetError(theLabel, 'Execute Error')
            return False

        DataLabelState.SetOK(theLabel)
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

    def GetStateMsg(self, theLabel)->str:
        return DataLabelState.GetMsg(theLabel)

    def IsDirectChanged(self, theLabel:Label):
        '''
            是否为直接参数节点
        '''
        return False

    def _isInit(self, theLabel:Label):
        return theLabel.HasAttribute()

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
    def myInit(self, theLabel: Label, theData=None):
        if theData is None:
            theData = '0'
        Logger().info(f'Init Label:{theLabel.GetEntry()}.value, {None}, {theData}')
        attr:Param = self.Attributes['value']
        attr.SetValue(theLabel, theData)
        return True

    def myChange(self, theLabel: Label, theData):
        attr:Param = self.Attributes['value']
        if theData == '':
            theData = '0.0'

        if attr.SetValue(theLabel, theData):
            return True
        return False

    def myValue(self, theLabel: Label):
        return self.Attributes['value'].GetValue(theLabel)

    def myTextValue(self, theLabel: Label):
        return str(self.myValue(theLabel))

    def IsDirectChanged(self, theLabel:Label):
        return True

    def GetTextValue(self, theLabel:Label):
        return self.myTextValue(theLabel)

class ShapeRefDriver(DataDriver):
    OutputType = DataEnum.Shape

    def __init__(self) -> None:
        super().__init__()
        self.Attributes['ref'] = Param(Attr_ShapeRef.GetID())

    def myInit(self, theLabel: Label, text=None)->bool:
        if text is None:
            Attr_ShapeRef.Set(theLabel)
            DataLabelState.SetError(theLabel, 'Need True ref Entry', True)
            return False

        anEntry = RP_AsciiStr(text)
        aRefLabel = Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, aRefLabel)
        Attr_ShapeRef.Set(theLabel, aRefLabel)
        return True

    def myChange(self, theLabel:Label, theData):
        
        # 过滤, 只允许引用Entry相对小的
        if theData == theLabel.GetEntry():
            return False

        anEntry = RP_AsciiStr(theData)
        aRefLabel = Label()
        TDF_Tool.Label(theLabel.Data(), anEntry, aRefLabel)
        if aRefLabel.IsNull() or aRefLabel.IsRoot() or aRefLabel == theLabel:
            DataLabelState.SetError(theLabel, 'Need True ref Entry', True)
            Logger().warning(f'Ref {anEntry} IsError')
            return False

        shapeRef_attr:Attr_ShapeRef = self.Attributes['ref'].GetAttribute(theLabel)
        if shapeRef_attr:
            shapeRef_attr.Remove()

        Logger().info(f'{theLabel.GetEntry()} ref {aRefLabel.GetEntry()} ')
        Attr_ShapeRef.Set(theLabel, aRefLabel)
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        return True

    def myValue(self, theLabel: Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            aDriver = reflabel.GetDriver()
            value = aDriver.GetValue(reflabel)
            return value

        Logger().warn(f'Entry:{theLabel.GetEntry()} not found reference')
        return None

    def IsDirectChanged(self, theLabel:Label):
        return True

    def GetRefLabel(self, theLabel:Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            return reflabel

        Logger().warning(f'Entry:{theLabel.GetEntry()} not found reference')
        return None

    def myTextValue(self, theLabel: Label):
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            return str(reflabel.GetEntry())
    
        Logger().warning(f'Entry:{theLabel.GetEntry()} not found reference')
        return 'Null'

    def GetTextValue(self, theLabel:Label):
        return self.myTextValue(theLabel)

    def GetArguLabel(self, theLabel: Label) -> list[Label]: # 依赖
        label_li = list()
        reflabel = self.Attributes['ref'].GetValue(theLabel)
        if reflabel:
            label_li.append(reflabel)

        return label_li

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

        self.Attributes['size'] = Param(TDataStd_Integer.GetID())

        self._ArrayFirstTag = 125
        self._SubTypeId = Sym_PntDriver_GUID
        # self._ID = driverID

    @property
    def StartIndex(self):
        return self._ArrayFirstTag

    def GetSize(self, theLabel: Label):
        aInt = theLabel.GetAttrValue(self.Attributes['size'].id)
        return aInt

    def GetChildAndName(self, theLabel:Label, ind: int):
        aDriver:DataDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)
        name = aDriver.Type+'_'+str(ind)

        return name, theLabel.FindChild(ind+self.StartIndex, False)

    def myInit(self, theLabel:Label, size=None):
        if size is None:
            size = '0'

        self.Attributes['size'].SetValue(theLabel, size)
        return True

    def myChange(self, theLabel:Label, size):
        start = self.StartIndex
        oldsize = self.GetSize(theLabel)
        size = int(size)
        if size > oldsize:
            for ind in range(oldsize, size):
                sub = theLabel.FindChild(start+ind, True)
                aDriver:DataDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)
                aDriver.Init(sub)
                # Exist.SetExist(sub)

        elif size < oldsize:
            for ind in range(size, oldsize):
                sub = theLabel.FindChild(start+ind, False)
                # Exist.SetDelete(sub)

        TDataStd_Integer.Set(theLabel, size)
        return True

    def GetArguLabel(self, theLabel: Label) -> list[Label]:
        sublabel_li = list()
        size = self.GetSize(theLabel)
        start = self.StartIndex
        
        for ind in range(start, size+start):
            sublabel_li.append(theLabel.FindChild(ind))

        return sublabel_li

    def GetNamedArgument(self, theLabel: Label) -> dict[str, Label]:
        sublabel_li = dict()
        size = self.GetSize(theLabel)
        start = self.StartIndex
        aDriver:DataDriver = DataDriverTable.Get().GetDriver(self._SubTypeId)

        for ind in range(0, size):
            name = aDriver.Type+'_'+str(ind)
            sublabel_li[name] = (theLabel.FindChild(ind+start))

        return sublabel_li

    def myTextValue(self, theLabel: Label):
        return str(self.Attributes['size'].GetValue(theLabel))

    def IsDirectChanged(self, theLabel:Label):
        return True

class CompoundDriver(DataDriver):
    def myInit(self, theLabel: Label, data:dict=None):
        flag = True
        for name, argu in self.Arguments.items():
            argu:Argument
            aLabel = theLabel.FindChild(argu.Tag, True)
            aDriver:DataDriver = DataDriverTable.Get().GetDriver(argu.DriverID)
            subData = None
            if data:
                subData = data.get(name, None)
            if not aDriver.Init(aLabel, subData):
                flag = False

        return flag

    def myChange(self, theLabel: Label, theData):
        if not isinstance(theData, dict):
            Logger().info(f'Entry:{theLabel.GetEntry()}, change failed with data:{theData}')
            return False

        for name, subData in theData.items():
            argu:Argument = self.Arguments[name]
            aLabel = theLabel.FindChild(argu.Tag)
            aDriver:DataDriver = aLabel.GetDriver()
            if not aDriver.Change(aLabel, subData):
                return False

        return True
