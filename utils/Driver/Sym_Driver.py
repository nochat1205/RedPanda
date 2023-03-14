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
    FromText
    
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
        Logger().debug("IDA:"+str(obj))
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
    def __init__(self, tag:TagResource, id:Standard_GUID) -> None:
        self._tag = tag.GetNewTag()
        self._driverID = id

    @property
    def Tag(self):
        return self._tag

    @property
    def DriverID(self):
        return self._driverID

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

    def Init(self, L: TDF_Label) -> bool:
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

        attr = self.myAttr
        aType = attr.Type
        aType.Set(L)
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
        else:
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

# class TOcafFunction_CutDriver(TFunction_Driver):
#     """_summary_
#     This driver class provide services around function execution. 
#     One instance of this class is built for the whole session. 
#     The driver is bound to the DriverGUID in the DriverTable class. 
#     It allows you to create classes which inherit from this abstract class. 
#     These subclasses identify the various algorithms which can be applied to the data 
#     contained in the attributes of sub-labels of a model. 
#     A single instance of this class and each of its subclasses is built for the whole session.

#     """
#     def __init__(self) -> None:
#         pass
    
#     def GetID():
#         return Standard_GUID("22D22E52-D69A-11d4-8F1A-0060B0EE18E8")

#     """验证对象标签、其参数和结果。"""
#     def Validate(self, log: TFunction_Logbook) -> None:
#         log.SetValid(self.Label(), True)

#         # !我们调用此方法来检查对象是否已被修改为要调用。
#         # !如果修改了对象标签或参数，我们必须重新计算对象 - 调用方法 Execute（）。

#     def MustExecute(self, log: TFunction_Logbook) -> bool:
#         if log.IsModified(self.Label()):
#             return True
#         """
#         # Cut (in our simple case) has two arguments: The original shape, and the tool shape.
#         # They are on the child labels of the cut's label:
#         # So, OriginalNShape  - is attached to the first  child label
#         #     ToolNShape - is attached to the second child label,
#         #     .
#         # Let's check them:
#         """
#         originalRef = TDF_Reference()
#         # TDF_Label aLabel = Label().FindChild(1);
#         #  BOOL f = Label().IsNull();
#         #  int a = Label().NbChildren();
#         aEntry = TCollection_AsciiString()
#         TDF_Tool_Entry(self.Label(), aEntry)
        
#         aLabel = self.Label()
#         aLabel.FindChild(1).FindAttribute(TDF_Reference.GetID(), originalRef)
#         if log.IsModified(originalRef.Get()):
#             return True
    
#         ToolRef = TDF_Reference()
#         aLabel.FindChild(2).FindAttribute(TDF_Reference.GetID(), ToolRef)
#         if log.IsModified(ToolRef.Get()):
#             return True

#         return False

#     def Execute(self, log: TFunction_Logbook) -> int:
#         # Let's get the arguments (OriginalNShape, ToolNShape of the object):

#         # First, we have to retrieve the TDF_Reference attributes to obtain
#         # the root labels of the OriginalNShape and the ToolNShape:
#         OriginalRef = TDF_Reference()
#         ToolRef = TDF_Reference()

#         aLabel = self.Label()
#         if not aLabel.FindAttribute(TDF_Reference.GetID(), OriginalRef):
#             return 1
#         OriginalLab = OriginalRef.Get()

#         if not aLabel.FindChild(2).FindAttribute(TDF_Reference.GetID(), ToolRef):
#             return 1
#         ToolLab = ToolRef.Get()


#         # Get the TNaming_NamedShape attributes of these labels
#         OriginaNShape = TNaming_NamedShape()
#         ToolNShape = TNaming_NamedShape()
#         if not OriginalLab.FindAttribute(TNaming_NamedShape.GetID(), OriginaNShape):
#             raise Standard_Failure("TOcaf_Commands::CutObjects")

#         if not ToolNShape.FindAttribute(TNaming_NamedShape.GetID(), ToolNShape):
#             raise Standard_Failure("TOcaf_Commands::CutObjects")

#         # Now, let's get the TopoDS_Shape of these TNaming_NamedShape:
#         OriginalShape = OriginaNShape.Get()
#         ToolShape = OriginaNShape.Get()
    
#         # STEP 2:
#         # Let's call for algorithm computing a cut operation:
#         mkCut = BRepAlgoAPI_Cut(OriginalShape, ToolShape);
#         # Let's check if the Cut has been successful:
#         if not mkCut.IsDone():
#             # QMessageBox.critical(qApp.activeWindow())
#             # QObject.tr("Cut Function Driver")
#             # QObject.tr("Cut not done")
#             return 2

#         ResultShape = mkCut.Shape()

#         # Build a TNaming_NamedShape using built cut
#         B = TNaming_Builder(self.Label())
#         B.Modify(OriginalShape, ResultShape)
#         # That's all:
#         # If there are no any mistakes we return 0:
#         return 0

# class TOcafFunction_CylDriver(TFunction_Driver):
#     def __init__(self) -> None:
#         return 

#     def GetID():
#         return Standard_GUID("22D22E53-D69A-11d4-8F1A-0060B0EE18E8")

#     def Validate(self, log: TFunction_Logbook) -> None:
#         log.SetValid(self.Label(), True)

#     def MustExecute(self, log: TFunction_Logbook) -> bool:
#         # If the object's label is modified:
#         if log.IsModified(self.Label()):
#             return True

#         # Cylinder (in our simple case) has 5 arguments:
#         # Let's check them:
#         aLabel:TDF_Label = self.Laebl()
#         if log.IsModified(aLabel.FindChild(1)):
#             return True # radius

#         if log.IsModified(aLabel.FindChild(2)):
#             return True # height

#         if log.IsModified(aLabel.FindChild(3)):
#             return True # x

#         if log.IsModified(aLabel.FindChild(4)):
#             return True # y

#         if log.IsModified(aLabel.FindChild(5)):
#             return True # z


#         return False


#     def Execute(self, log: TFunction_Logbook) -> int:
#         TSR = TDataStd_Real()
#         x, y, z, r, h = Standard_Real(), Standard_Real(), Standard_Real()\
#             ,Standard_Real(), Standard_Real()
#         aLabel:TDF_Label = self.Label()

#         if not aLabel.FindChild(1).FindAttribute(TDataStd_Real.GetID(), TSR):
#             return 1
#         r = TSR.Get()

#         if not aLabel.FindChild(2).FindAttribute(TDataStd_Real.GetID(), TSR):
#             return 1
#         h = TSR.Get()
        
#         if not aLabel.FindChild(3).FindAttribute(TDataStd_Real.GetID(), TSR):
#             return 1
#         x = TSR.Get()

#         if not aLabel.FindChild(4).FindAttribute(TDataStd_Real.GetID(), TSR):
#             return 1
#         y = TSR.Get()

#         if not aLabel.FindChild(5).FindAttribute(TDataStd_Real.GetID(), TSR):
#             return 1
#         z = TSR.Get()

#         mkCyl = BRepPrimAPI_MakeCylinder(gp_Pnt(x, y, z), gp_Dir(0, 0, 1), r, h)
#         ResultShape = mkCyl.Shape()
#         return 0

