
class CSet:
    """A command set
    
    Properties:
        - commands: a set of Command object
        
    Usage:
        x = CSet({c1, c2})
    """
    
    def __init__(self, commands):
        assert isinstance(commands, set)
        self.commands = commands


    def as_string(self):
        """Return a string representation of the object"""
        s = ', '.join([c.as_string() for c in self.commands])
        return "{" + s + "}"
    

    def slow_equals(self, other, reversed=False):
        """Whether this set of commands is equivalent to another one. Only for testing"""
        me = list(self.commands)
        for i, c in enumerate(me):
            for i2, c2 in enumerate(me):
                if i != i2 and c.equals(c2):
                    raise Exception("Duplicate command in set")
        
        for c in self.commands:
            for c2 in other.commands:
                if c.equals(c2):
                    break
            else:
                return False
        
        if reversed:
            return True
        else:
            return other.slow_equals(self, reversed=True)
