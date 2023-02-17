
class Command:
    """Class representing a filesystem command.
    
    Properties:
        - node: a Node object
        - before: a Value object; the input value
        - after: a Value object; the output value
        - prev: an optional pointer to another command in a double-linked list
        - next: an optional pointer to another command in a single-linked list
        - up: an optional up pointer to another command
        - order: an optional index used during ordering
        - delete: optional bool flag used by get_any_merger(): whether the current command is discarded
    
    Usage:
        c = Command(node, before_value, after_value)
    """
    
    def __init__(self, node, before, after):
        """Constructor.
        
        Arguments:
            - node: a Node object
            - before: a Value object; the input value
            - after: a Value object; the output value
        """
        self.node = node
        self.before = before
        self.after = after
        self.prev = None
        self.next = None
        self.up = None
        self.order = None
        self.delete = None


    def as_string(self, color=False):
        """Return a string representation of the object"""
        if color:
            on = "\033[31;1m"
            off = "\033[0m"
        else:
            on = ''
            off = ''
        return f"{on}<{off}{self.node.as_string()}{on}|{off}{self.before.as_string()}{on}|{off}{self.after.as_string()}{on}>{off}"


    def clone(self):
        """Return a clone excluding the pointers specific to a command in a list"""
        return Command(self.node, self.before, self.after)
        
        
    def equals(self, other):
        """Whether the current object and another are equal"""
        return (self.node.equals(other.node) and self.before.equals(other.before) and self.after.equals(other.after))

    
    def is_null(self):
        """Whether this is a null command"""
        return self.before.equals(self.after)

    
    def is_constructor(self):
        """Whether this is a constructor command"""
        return self.after.type_greater(self.before)

    
    def is_destructor(self):
        """Whether this is a destructor command"""
        return self.after.type_less(self.before)
    
    
    def is_constructor_pair_with_next(self, other):
        """Whether this command forms a constructor pair with the next command, `other`"""
        return (self.is_constructor() and self.after.is_dir() and other.is_constructor() and other.before.is_empty() and self.node.is_parent_of(other.node))
    
    
    def is_destructor_pair_with_next(self, other):
        """Whether this command forms a destructor pair with the next command, `other`"""
        return (self.is_destructor() and self.after.is_empty() and other.is_destructor() and other.before.is_dir() and other.node.is_parent_of(self.node))


    def weak_conflict_with(self, other):
        """Whether this command is in conflict with another command, by the weak definition"""
        if self.equals(other):
            raise Exception("conflicts_with() should not be called on equal commands")
        if self.node.equals(other.node):
            return True
        
        if self.node.is_ancestor_of(other.node):
            ancestor = self
            descendant = other
        elif self.node.is_descendant_of(other.node):
            ancestor = other
            descendant = self
        else:
            return False

        if (not ancestor.after.is_dir()) and (not descendant.after.is_empty()):
            return True
        return False
        
