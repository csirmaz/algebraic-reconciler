
from cset import CSet
from command import Command
from node import Node
from value import Value

class CSequence:
    """A command sequence
    
    s = CSequence([c1, c2])
    """
    
    def __init__(self, commands):
        assert isinstance(commands, list)
        self.commands = commands
    
    
    def as_string(self):
        return '.'.join([c.as_string() for c in self.commands])
    
    
    def equals(self, other):
        """Whether the two sequences are equal"""
        if len(self.commands) != len(other.commands):
            return False
        for i in range(len(self.commands)):
            if not self.commands[i].equals(other.commands[i]):
                return False
        return True
    
    
    def order_by_node(self):
        """Return another sequence in which the commands are ordered by node; on equivalent nodes the original ordering is kept"""
        return self.order_by_node_bubble()
    
    
    def order_by_node_bubble(self):
        """Bubble sort implementation of order_by_node()"""
        commands = self.commands[:] # shallow clone
        changed = True
        while changed:
            changed = False
            for i in range(len(commands)-1):
                if commands[i].node.comp(commands[i+1].node) == 1:
                    commands[i], commands[i+1] = commands[i+1], commands[i]
                    changed = True
        return CSequence(commands)

    
    def get_canonical_set(self):
        """Return the canonical command set equivalent to this sequence.
        Note: We're not checking if the sequence is breaking"""
        prev_node = None
        prev_before = None
        out = set()
        commands = self.order_by_node().commands
        for i in range(len(commands)):
            c_this = commands[i]
            c_next = None
            if i < len(commands) - 1:
                c_next = commands[i+1]
            
            if prev_node is None:
                prev_node = c_this.node
                prev_before = c_this.before
                
            if c_next is None or not c_next.node.equals(prev_node):
                # End of current block of the same node
                c_new = Command(prev_node, prev_before, c_this.after)
                if not c_new.is_null():
                    out.add(c_new)
                prev_node = None
                prev_before = None
            
        return CSet(out)
    
    
    @classmethod
    def from_set(cls, cset):
        """Dumb function to turn a command set into a command sequence; the order of commands is not guaranteed"""
        return CSequence(list(cset.commands))

    
if __name__ == '__main__':
    
    # Test code
    c1 = Command(Node(['d1']), Value(Value.T_EMPTY, 'e'), Value(Value.T_DIR, 'D1'))
    c2 = Command(Node(['d1', 'd2']), Value(Value.T_EMPTY, 'e'), Value(Value.T_DIR, 'D2'))
    c2b = Command(Node(['d1', 'd2']), Value(Value.T_EMPTY, 'e'), Value(Value.T_DIR, 'D2b'))
    c3 = Command(Node(['d1', 'd2', 'f3']), Value(Value.T_EMPTY, 'e'), Value(Value.T_FILE, 'F'))
    s = CSequence([c1, c2, c2b, c3])
    s2 = CSequence([c3, c2, c1, c2b])
    sc = CSequence([c1, c2b, c3])
    assert s2.order_by_node().equals(s)
    assert CSequence.from_set(s2.get_canonical_set()).order_by_node().equals(sc)
    print("Tests done")
    
