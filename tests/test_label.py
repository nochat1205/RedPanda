import os,sys                                     
sys.path.append(os.getcwd()) 
import pytest

from OCC.Core.TDF import (
    TDF_Data
)

from RedPanda.RPAF.RD_Label import Label

def test_label():
    
    label = Label()
    assert label.__hash__()
