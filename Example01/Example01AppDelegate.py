#
#  Example01AppDelegate.py
#  Example01
#
#  Created by Patrick Dwyer on 1/19/11.
#

from Foundation import *
from AppKit import *
from objc import IBOutlet, IBAction

from PredicateUtility import *

class Example01AppDelegate(NSObject):

    editor = IBOutlet()
    
    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")
        
        # create the editor
        self.predicateManager = PredicateEditorManager.alloc().initWithPredicateEditor_(self.editor)

        # add a few search criteria
        self.predicateManager.addMappedCriteria("First Name", "firstname", operators = [PredicateEditorManager.OP_EQ, PredicateEditorManager.OP_BEGINSWITH])
        self.predicateManager.addMappedCriteria("Last Name", "lastname", operators = [PredicateEditorManager.OP_NE, PredicateEditorManager.OP_CONTAINS])
        self.predicateManager.addCriteria("zipcode")
        
        # build the predicate manager
        self.predicateManager.build()
        self.predicateManager.addRow()
        
    @IBAction
    def generateSQL_(self, id):
        NSLog("Generating SQL from Predicate Editor")
        print "sql:\n\t",self.predicateManager.wrappedPredicate().toSQL() 