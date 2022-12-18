
class Command:
    
    def __init__(self, node, before, after):
        self.node = node # a Node object`
        self.before = before # a Value object
        self.after = after # a Value object
        
    def as_string(self):
        return f"<{self.node.as_string()}, {self.before.as_string()}, {self.after.as_string()}>"
        
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
