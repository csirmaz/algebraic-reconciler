
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


    def as_string(self):
        """Return a string representation of the object"""
        return f"<{self.node.as_string()}, {self.before.as_string()}, {self.after.as_string()}>"


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

        
