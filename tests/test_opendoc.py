import os,sys
sys.path.append(os.getcwd())

from RedPanda.RPAF.Application import Application


def test():
    app = Application()
    path = r'D:\2022-1\graduate_design\RedPanda\resource\c.rpxml.xml'
    app.OpenDoc(path)


if __name__ == '__main__':
    test()
