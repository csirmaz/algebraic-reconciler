
import functools

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
        # Bubble sort for now
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
        """Return the canonical command set equivalent to this sequence"""
        prev = None
        out = set()
        for c in self.order_by_node().commands:
            # Skip null commands
            if c.is_null():
                continue
            # Skip commands on the same nodes
            if prev is None:
                prev = c
                continue
            else:
                if prev.node.equals(c.node):
                    prev = Command(c.node, prev.before, c.after)
                else:
                    out.add(prev)
                    prev = c
        if prev is not None:
            out.add(prev)
        return CSet(out)
    
    @classmethod
    def from_set(cls, cset):
        """Dumb function to turn a command set into a command sequence"""
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
    
