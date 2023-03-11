from widgets.Logic_Construct import Logic_Construct

class Sym_NewShapeData(object):
    def __init__(self, theInput:Logic_Construct):
        self.driverID = theInput.driverId
        self.dict_params:dict = self.GetParams(theInput)
        print(self.dict_params)
        self.ParentPath = self.dict_params['Parent']
        self.name = self.dict_params["Name"]

    @staticmethod
    def GetParams(theInput:Logic_Construct):
        dict_lines = theInput.dict_lineParam
        dict_params = dict()
        for name, lineEdit in dict_lines.items():
            dict_params[name] = lineEdit.text()
        return dict_params
