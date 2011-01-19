About
=====
PredicateUtility is a small collection of classes for efficient and easy management 
of NSPredicateEditors and NSPredicates when creating Cocoa apps with Python. These
classes rely upon the PyObjC bridge.

These classes arose out of a need to generate SQL WHERE clauses from NSPredicates; a
task that is handled automatically when using Cocoa and CoreData bindings, but unavailable
when using non-managed databases.

The following classes are defined in PredicateUtility:
	
- PredicateEditorManager - Configure and control a NSPredicateEditor
- PredicateWrapper - Deconstruct an NSPredicate (or subclass) into a SQL snippit
- PredicateError - General purpose Exception when working with PredicateUtility classes

Example Application
-------------------
The _Example 01_ application is a barebones NSApplication based app that generates SQL
snippits from aribitrarily nested NSPredicates taken from an NSPredicateEditor. You can
nest NSPredicateEditor rows by holding the _option_ key while clicking on the _+_ button
of an NSPredicateEditor row.

Terminology
-----------
The PredicateUtility classes use the terminology _column_ and _criteria_ when describing configuring,
displaying, and deconstructing NSPredicate objects. In this context _column_ refers to a SQL column
name, such as "column1". It is assumed that the _column_ name is a valid SQL identifier. The _criteria_
refer to how a _column_ is configured to be queried in an NSPredicateEditor, and includes the
operators that can be used, and the type of the column (currently PredicateUtility only supports an
implicit "string" type).

How To
======

PredicateEditorManager and PredicateWrapper
-------------------------------------------
Given an IBOutlet linked to an NSPredicateEditor, the following code in the Application Delegate
creates the PredicateEditorManager, configures the columns to be used in the PredicateEditor, sets 
up the UI, and generates SQL when a button callback is triggered:

	from Foundation import *
	from AppKit import *
	from objc import IBOutlet, IBAction
	
	from PredicateUtility import *
	
	class Example01AppDelegate(NSObject):
	
		editor = IBOutlet()
		
		def applicationDidFinishLaunching_(self, sender):
			
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
			print "sql: ", self.predicateManager.wrappedPredicate().toSQL() 

There are a few things going on in this example. Firstly, the _PredicateEditorManager_ is created, using
the _initWithPredicateEditor__ initializer. Once the _PredicateEditorManager_ has been created, columns, 
or criteria for searching and building a predicate, can be added. In some cases the column for the search
is a simple name, like _zipcode_, which can be used in sql as a column name, and is easily understood
in the UI by a user. In this case the _addCriteria_ method can be used:
	
	self.predicateManager.addCriteria("zipcode")

The types of operators to use in comparing the _zipcode_ criteria could have been optionally included
as a named parameter:
	
	self.predicateManager.addCriteria("zipcode", operators = [PredicateEditorManager.OP_EQ, PredicateEditorManager.OP_NE])

In some cases the SQL column name is hard to understand, or a localized or "nice" version of the column
name is know. An alternate method can be used to configure a criteria with a display name different
from it's SQL name:
	
	self.predicateManager.addMappedCriteria("First Name", "firstname", operators = [PredicateEditorManager.OP_EQ, PredicateEditorManager.OP_BEGINSWITH])

Here the SQL column _firstname_ will be displayed in the UI as _First Name_, but SQL generated from
the PredicateWrapper will contain the proper _firstname_ column name.

The following operators are currently supported (with the Cocoa equivalent type in parenthesis):
- OP_EQ (NSEqualToPredicateOperatorType) - column equal to
- OP_NE (NSNotEqualToPredicateOperatorType) - column not equal to
- OP_CONTAINS (NSContainsPredicateOperatorType) - column contains value
- OP_BEGINSWITH (NSBeginsWithPredicateOperatorType) - column begins with
- OP_ENDSWITH (NSEndsWithPredicateOperatorType) - column ends with

Just PredicateWrapper
---------------------
It is also possible to use the PredicateWrapper directly without needing an PredicateEditorWrapper. If
you have an NSPredicate object (or subclass), you can convert it to SQL with a PredicateWrapper:
	
	predicate = <get an NSCompoundPredicate from somewhere>
	wrapper = PredicateWrapper(predicate)
	print wrapper.toSQL()

Because _criteria_ are never specified it is not possible to use mapped column names in this instance.

Limitations
-----------
So far these classes only support the most basic features of NSPredicates and NSPredicateEditor. The
only data type that can be used in the NSPredicateEditor is the _String_ type.

Incremental improvements will be made to these classes as needed; or if you have a feature
you'd like to see sooner rather than later, please contact me.

License & Contact
-----------------
PredicateUtility and the included sample applications are released under an [Apache 2.0](http://www.opensource.org/licenses/apache2.0) license.

If you have questions, comments, or issues, please contact me patricknevindwyer(@)gmail.com

