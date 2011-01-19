"""
PredicateUtility

author: Patrick Nevin Dwyer
url: https://github.com/patricknevindwyer/PredicateUtility
license: Apache 2.0 (http://www.opensource.org/licenses/apache2.0)
date: 2011.01.19
python version: 2.6.1

PredicateUtility builds on the PyObjC Python/Cocoa bindings to create an
easy to use, easy to configure set of classes for managing NSPredicateEditors
and extracting complex query statements from NSPredicates. The initial use case of
these classes was creating an NSPredicateEditor for building complex SQL WHERE
clauses.

When using Cocoa bindings to Core Data NSPredicates are automatically converted
to the necessary SQL for extracting managed data. Facilities do not exist, however,
to generate the raw SQL from NSPredicates for use in non-managed databases. The
classes in PredicateUtility can be used to generate this raw SQL.
"""
import types

from Foundation import NSObject, NSCompoundPredicate, NSNotPredicateType, NSOrPredicateType, NSAndPredicateType, NSComparisonPredicate, NSPredicate
from CoreData import NSStringAttributeType, NSEqualToPredicateOperatorType, NSNotEqualToPredicateOperatorType, NSContainsPredicateOperatorType, NSBeginsWithPredicateOperatorType, NSEndsWithPredicateOperatorType
from AppKit import NSPredicateEditorRowTemplate

class CriteriaError(Error):
	def __init__(self, msg):
		self.msg = msg
	def __repr__(self):
		return str(self.msg)
		
class PredicateEditorManager(NSObject):
	"""
	The PredicateEditorManager controls the configuration of the NSPredicateEditor, and
	the extraction of formatted query strings from the Editor. The Cocoa types used by
	the NSPredicateManager are mapped to type names supported by the PredicateEditorManager,
	unsupported types will throw an error:
		
		NSStringAttributeType - PredicateEditorManager.STRING
		
	"""
	STRING = NSStringAttributeType
	
	OP_EQ = NSEqualtoPredicateOperatorType
	OP_NE = NSNotEqualToPredicateOperatorType
	OP_CONTAINS = NSContainsPredicateOperatorType
	OP_BEGINSWITH = NSBeginsWithPredicateOperatorType
	OP_ENDSWITH = NSEndsWithPredicateOperatorType
	
	_supportedOperatorTypes = [OP_EQ, OP_NE, OP_CONTAINS, OP_BEGINSWITH, OP_ENDSWITH]
	_supportedColumnTypes = [STRING]
	
	def init(self):
		"""
		Initialize a new Manager for an NSPredicateEditor
		"""
		self = super(MyClass, self).init()
		if self is None: return None
		
		self._initialize()
		
		return self
		
	def initWithPredicateEditor_(self, predicateEditor):
		"""
		Initialize with an NSPredicateEditor
		"""
		self = super(MyClass, self).init()
		if self is None: return None
		
		self._initialize()
		self._editor = predicateEditor
		
		return self
		
	def _initialize(self):
		"""
		Common initialization
		"""
		# setup our local data
		self._criteria = []
		self._editor = None
		self._isNesting = True
		
	def addCriteria(self, criteria, criteriaType=PredicateEditorManager.STRING, operators=[PredicateEditorManager.OP_EQ]):
		"""
		Add a search criteria to the NSPredicateEditor. Optionally specify
		the type of this criteria (defaults to String) and supported operators.
		
		Example:
			
			manager = PredicateEditorManager.alloc().init()
			manager.addCriteria("column1")
			manager.addCriteria("column2", operators = [manager.OP_BEGINSWITH, manager.OP_ENDSWITH])
			
		"""
		self.addMappedColumn(criteria, criteria, criteriaType=criteriaType, operators=operators)
	
	def addMappedCriteria(self, niceName, backingName, criteriaType=PredicateEditorManager.STRING, operators=[PredicateEditorManager.OP_EQ]):
		"""
		Add a search criteria using a 'nice' name mapped to the actual criteria name. This makes
		it fairly simple to have localized readable names mapped to backing column names that
		remain constant.
		
		Example:
			
			manager = PredicateEditorManager.alloc().init()
			
			# provide a better formatted name for display of the 'column1' column
			manager.addMappedCriteria("Column 1", "column1")
			
			manager.addMappedCriteria("Last Name", "lname_ascii", operators = [manager.OP_CONTAINS, manager.OP_EQ, manager.OP_NE])
		
		"""
		if criteriaType not in PredicateEditorManager._supportedColumnTypes:
			raise CriteriaError("Unsupported criteria type specified")
			
		self._criteria.append(
			{
				'displayName': niceName,
				'backingName': backingName,
				'type': criteriaType,
				'operators': operators
			}
		)
		
	def isNesting(self, nesting = None):
		"""
		Does the predicate editor support nested (AND OR NOT) queries.
		"""
		return self._isNesting

	def setIsNesting(self, nesting = True):
		"""
		Set the Predicate Editor support for nested (AND OR NOT) queries.
		"""
		self._isNesting = nesting
		
	def setPredicateEditor(self, ed):
		"""
		Set the NSPredicateEditor associated with this Manager
		"""
		self._editor = ed
	
	def predicateEditor(self):
		"""
		Get the associated NSPredicateEditor
		"""
		return self._editor
		
	def build(self):
		"""
		Build and configure the NSPredicatEditor using the configured criteria.
		"""
		predicateSet = []
		
		# if nesting is supported we first add the compound type predicate
		if self._isNesting:
			basePred = NSPredicateEditorRowTemplate.alloc().initWithCompoundTypes_([2, 1])
			predicateSet.append(basePred)
		
		# now convert each criteria into a predicate template
		for criteria in self._criteria:
			lexp = [NSExpression.expressionForConstantValue_(criteria['displayName'])]
			ops = [NSNumber.numberWithUnsignedInt_(i) for i in criteria['operators']]
			predicate = NSPredicateEditorRowTemplate.alloc().initWithLeftExpressions_rightExpressionAttributeType_modifier_operators_options_(
				lexp,
				criteria['type'],
				NSAnyPredicateModifier,
				ops,
				0
			)
			predicateSet.append(predicate)
		
		# set the final predicate templates
		self._editor.setRowTemplates_(predicateSet)

	def predicate(self):
		"""
		Retrieve the NSPredicate from the NSPredicateEditor representing the current compound
		predicate state.
		"""
		return self._editor.predicate()
	
	def wrappedPredicate(self):
		"""
		Retrieve the NSPredicate of the NSPredicateEditor wrapped in a PredicateWrapper
		object. This is a convenience method identical to:
			
			pred = manager.predicate()
			criteria = manager.criteria()
			wpred = PredicateWrapper(pred, criteria = criteria)
			
		"""
		return PredicateWrapper(self.predicate())
		
class PredicateWrapper(object):
	"""
	The PredicateWrapper class provides methods for decomposing NSPredicate objects (and subclasses,
	specifically NSCompoundPredicate) into SQL WHERE clauses.
	"""
	
	OPERATORS = {
		NSEqualToPredicateOperatorType: {'op': "=", 'format': "%s"},
		NSNotEqualToPredicateOperatorType: {'op': "!=", 'format': "%s"},
		NSBeginsWithPredicateOperatorType: {'op': "LIKE", 'format': "%s%%"},
		NSEndsWithPredicateOperatorType: {'op': "LIKE", 'format': "%%%s"},
		NSContainsPredicateOperatorType: {'op': "LIKE", 'format': "%%%s%%"}
	}

	def __init__(self, pred, criteria=None):
		"""
		Create a PredicateWrapper around an NSPredicate
		"""
		self._predicate = pred
		self._criteria = criteria
		
	def criteria(self):
		"""
		Retrieve the criteria used when evaluating an NSPredicate conversion.
		"""
		return self._criteria
		
	def setCriteria(self, criteria):
		"""
		Set the criteria used in the construction of the NSPredicate. These criteria are used to
		determine the actual column name (in the case of mapped columns) and the column Type.
		"""
		self._criteria = criteria
	
	def toSQL(self):
		"""
		Convert the wrapped NSPredicate into a SQL statement that can be used in a WHERE
		clause.
		"""
		sql = self._toSQL(self._predicate)
		
		return sql
	
	def _toSQL(self, fpred):
		"""
		Internal recursive method for decomposing NSPredicate objects. This method should never
		be directly called. Instead, call PredicateWrapper::toSQL()
		"""
		if type(fpred) == NSCompoundPredicate:
            
            compoundType = fpred.compoundPredicateType()
            compoundOp = None
            
            if compoundType == NSNotPredicateType:
                compoundOp = ' NOT '
            elif compoundType == NSAndPredicateType:
                compoundOp = ' AND '
            elif compoundType == NSOrPredicateType:
                compoundOp = ' OR '
            
            subClauses = []
            for spred in fpred.subpredicates():
                subClauses.append(self._toSQL(spred))
            
            return "(" + compoundOp.join(subClauses) + ")"
        elif type(fpred) == NSPredicate:
        
        	# shouldn't ever really hit this directly
            print "NSPredicate"
            
        elif type(fpred) == NSComparisonPredicate:
            
            # find the comparison column
            lexp = fpred.leftExpression().constantValue()
            compCol = self._backingNameForDisplayName(lexp)
            
            # find the sql comparator
            mappedOp = self.OPERATORS[fpred.predicateOperatorType()]

            op = mappedOp['op']
			rexp = mappedOp['format'] % (fpred.rightExpression().constantValue())
			
            print "NSComparisonPredicate"
            print "\tleft: ", compCol
            print "\top: ", op
            print "\tright: ", rexp
            
            return "%s %s \"%s\"" % (compCol, op, rexp)
        else:
            print "Unknown predicate type: ", type(fpred)
            
    def _backingNameForDisplayName(self, dn):
    	"""
    	Retrieve the backing criteria name for a given display name.
    	"""
    	
    	for criteria in self._criteria:
    		if criteria['displayName'] == dn:
    			return criteria['backingName']
    	
    	return None