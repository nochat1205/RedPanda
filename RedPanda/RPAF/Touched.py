from .RD_Label import Label

class TouchedLabel:
    Touched_set = set()
    
    @staticmethod
    def Done():
        TouchedLabel.Touched_set.clear()

    @staticmethod
    def SetTouched(theLabel:Label):
        TouchedLabel.TouchedList.add(theLabel)

    @staticmethod
    def GetTouched():
        return TouchedLabel.Touched_set.copy()
