from OCC.Core.TDocStd import TDocStd_Application
from OCC.Core.TDF import TDF_TagSource
from OCC.Core.XmlDrivers import xmldrivers


from RedPanda.logger import Logger
from RedPanda.Core.data import RP_ExtendStr

from .DriverTable import DataDriverTable
from .DataDriver import *
from .GUID import RP_GUID
from .Attribute import TDataStd_Name
from .Document import Document
from .RD_Label import Label


class Application(TDocStd_Application):
    def __init__(self) -> None:
        super(Application, self).__init__()
        self._main_doc = None

        self.doc_li = list()
        self._registerDriver()

        xmldrivers.DefineFormat(self)        

    def _registerDriver(self):
        # Instantiate a Driver and add it to the DriverTable
        DataDriverTable.Get().AddDriver(RealDriver.ID,
                                              RealDriver())
        DataDriverTable.Get().AddDriver(PntDriver.ID,
                                              PntDriver())
        DataDriverTable.Get().AddDriver(TransformDriver.ID,
                                              TransformDriver())
        DataDriverTable.Get().AddDriver(BoxDriver.ID,
                                              BoxDriver())
    
        DataDriverTable.Get().AddDriver(ShapeRefDriver.ID,
                                              ShapeRefDriver())
        DataDriverTable.Get().AddDriver(CutDriver.ID,
                                              CutDriver())
        DataDriverTable.Get().AddDriver(PntArrayDriver.ID,
                                              PntArrayDriver())
        DataDriverTable.Get().AddDriver(BezierDriver.ID,
                                              BezierDriver())
        DataDriverTable.Get().AddDriver(BezierDriver.ID,
                                              BezierDriver())
        DataDriverTable.Get().AddDriver(TransShapeDriver .ID,
                                              TransShapeDriver())

        from .DataDriver.VertexDriver import Pnt2dDriver
        DataDriverTable.Get().AddDriver(Pnt2dDriver .ID,
                                              Pnt2dDriver())

        from .DataDriver.ShapeBaseDriver import Ax2dDriver
        DataDriverTable.Get().AddDriver(Ax2dDriver .ID,
                                              Ax2dDriver())

        from .DataDriver.Geom2dDriver import Ellipse2dDriver
        DataDriverTable.Get().AddDriver(Ellipse2dDriver .ID,
                                              Ellipse2dDriver())

    def RegisterDriver(self, driver:DataDriver):
        DataDriverTable.Get().AddDriver(driver.ID, driver)

    def AddDocument(self, doc):
        self.InitDocument(doc)
        super(TDocStd_Application, self).Open(doc)

    def Update(self, theLabel:Label, str)->set:
        touched_set = set()
        update_set = set()
        Logger().info("-- NewConmand --")
        self._main_doc.NewCommand()
        # change
        aDriver:DataDriver = theLabel.GetDriver()
        aDriver.Change(theLabel, str)

        # link change
        update_set.add(theLabel)
        touched_set.add(theLabel)
        while len(update_set) > 0:
            aLabel = update_set.pop()
            aDriver:DataDriver = aLabel.GetDriver()
            if aDriver:    
                aDriver.Execute(aLabel)

                label_set = aDriver.GetRefMeLabel(aLabel)
                update_set |= label_set
                touched_set |= label_set

        self._main_doc.CommitCommand()
        Logger().info("-- commit command --")

        return touched_set

    def NewDataLabel(self, driverID:RP_GUID, data=None):
        self._main_doc.NewCommand()
        Logger().info("-- NewConmand --")        
        Logger().info("-- Add New Shape --")

        aDriver:DataDriver = DataDriverTable.Get().GetDriver(driverID)
        mainLabel = TDF_TagSource.NewChild(self._main_doc.Main())
        aDriver.Init(mainLabel, data)
        TDataStd_Name.Set(mainLabel, RP_ExtendStr('New '+aDriver.Type))

        self._main_doc.CommitCommand()

        Logger().info("-- commit command --")
        return mainLabel

    def NewDocument(self, theFormat:str):
        doc = Document(RP_ExtendStr(theFormat))
        self.AddDocument(doc)
        TDataStd_Name.Set(doc.Main(), RP_ExtendStr(str(doc)))

        # Set the maximum number of available "undo" actions
        doc.SetUndoLimit(10)

        self.doc_li.append(doc)
        self._main_doc = doc

        return doc

    def HaveDoc(self):
        return self._main_doc is not None

    def SaveDoc(self):
        url = self._main_doc.File()
        self.SaveAs(self._main_doc, RP_ExtendStr(url))
        # with open(url.replace('xml', 'bin'), 'wb+') as f:
        #     pickle.dump(self._main_doc, f)

    def OpenDoc(self, path):
        from OCC.Core.CDF import CDF_FWOSDriver, CDF_Application
        from OCC.Core.TCollection import TCollection_ExtendedString
        from OCC.Core.TDocStd import TDocStd_Document
        import os
        # driver = CDF_FWOSDriver()
        # mdata = driver.MetaData(
        #     TCollection_ExtendedString(os.path.dirname(path)),
        #     TCollection_ExtendedString(os.path.basename(path)))
        doc = self.Retrieve(
            TCollection_ExtendedString(os.path.dirname(path)),
            TCollection_ExtendedString(os.path.basename(path))
        )
        self._main_doc = TDocStd_Document.DownCast(doc)
        # print(type(doc))
        return self._main_doc
        doc = self.NewDocument(RP_ExtendStr('XmlOcaf'))
        doc.SetFile(path)

        try:
            self.Rebuild(path, doc)
        except Exception as error:
            Logger().error(str(error))

        # from OCC.Core.Message import Message_ProgressRange
        # doc = Document(RP_ExtendStr('XmlOcaf'))
        # self.Open(RP_ExtendStr (path), doc)

        return doc

    def Rebuild(self, path, doc:Document):
        from RedPanda.RPAF.DriverTable import DataDriverTable
        from RedPanda.Core.data import RP_ExtendStr
        from RedPanda.RPAF.GUID import RP_GUID
        from RedPanda.RPAF.RD_Label import Label
        from RedPanda.RPAF.Attribute import Lookup_Attr, FromText
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(path)
        root = tree.getroot()
        xmlns = r"{http://www.opencascade.org/OCAF/XML}"

        labeltag = xmlns+'label'
        nametag = xmlns+'TDataStd_Name'
        functiontag = xmlns+'TFunction_Function'
        shapetag = xmlns+'TNaming_NamedShape'
        statetag = xmlns+'TDataStd_Integer'
        realtag = xmlns+'TDataStd_Real'
        def todeep3(root):
            node = root
            # name 
            for _ in range(2):
                for child in node:
                    if child.tag == labeltag:
                        node = child
                        break

  
            return node

        def setDataLabel(node, theLabel:Label):
            from .Attribute import (
                TFunction_Function, Attr_State_guid, Attr_State,
                TDataStd_Comment, TDataStd_Real
            )
            from .DataDriver.BaseDriver import DataLabelState
            for child in node:
                print(child.tag)
                if child.tag in (shapetag,):
                    continue
                elif child.tag == functiontag:
                    id = RP_GUID( child.attrib['guid'])
                    TFunction_Function.Set(theLabel, id)
                elif (
                        child.tag == statetag 
                    and 'intattguid' in child.attrib
                    and RP_GUID(child.attrib['intattguid']) == Attr_State_guid
                ):
                    Attr_State.Set(theLabel, DataLabelState.ParamError)
                elif child.tag == nametag:
                    name = child.text
                    TDataStd_Name.Set(theLabel, RP_ExtendStr(name))
                elif child.tag == realtag:
                    TDataStd_Real.Set(theLabel, float(child.text))
                    print(float(child.text))

                elif child.tag == labeltag:
                    tag = int(child.attrib['tag'])
                    aLabel = theLabel.FindChild(tag, True)
                    setDataLabel(child, aLabel)
                else:
                    attr = child.attrib
                    value = child.text
                    idName = ['guid', 'nameguid', 'intattguid']
                    attr_id = None
                    for iname in idName: 
                        if iname in attr:
                            attr_id = RP_GUID( attr[iname])
                            break # for

                    if attr_id is None:
                        Logger().error(f'no none xml node {child.tag} {child.attrib}')
                        continue
                    
                    if attr_id == TDataStd_Comment.GetID():
                        TDataStd_Comment.Set(theLabel, RP_ExtendStr(value))
                        continue

                    cls = Lookup_Attr[attr_id]
                    if cls is None:
                        continue

                    cls.Set(theLabel, attr_id, FromText(cls.GetID(), value))

        # 遍历整个XML文件
        def traverse(element, prefix='|--'):
            # 处理当前元素
            if element.tag == nametag:
                return
            print(prefix, element.tag, element.attrib, element.text)

            # 处理当前元素的所有子元素
            for child in element:
                traverse(child, '  '+prefix)

        mainLabel = doc.Main()
        node = todeep3(root)
        # traverse(node)
        setDataLabel(node, mainLabel)
