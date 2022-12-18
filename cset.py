
class CSet:
    """A command set
    
    x = CSet({c1, c2})
    """
    
    def __init__(self, commands):
        assert isinstance(commands, set)
        self.commands = commands
        
