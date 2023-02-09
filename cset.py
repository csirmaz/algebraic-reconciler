
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
    
    
    def clone(self):
        """Return a clone"""
        return CSet({command.clone() for command in self.commands})
