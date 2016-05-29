'''
Created on May 13, 2016

@author: karl
'''
import unittest


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):import sys
from PySide.QtCore import *
from PySide.QtGui import *
 
class Form(QDialog):
 
 def __init__(self, parent=None):
 super(Form, self).__init__(parent)
 self.setWindowTitle("My Form")
 
 
if __name__ == '__main__':
 # Create the Qt Application
 app = QApplication(sys.argv)
 # Create and show the form
 form = Form()
 form.show()
 # Run the main Qt loop
 sys.exit(app.exec_())
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()