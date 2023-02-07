
from cset import CSet
from command import Command
from node import Node
from value import Value
from heapsort import heap_sort

class CSequence:
    """A single- or double-linked list of commands
    
    Properties:
        - start: the first Command object in the sequence, or False if the sequence is empty
        - end: the last Command object in the sequence, or False if the sequence is empty, or None if the sequence is single-linked
    
    Usage:
        s = CSequence([command1, command2])
    """
    
    def __init__(self, commands):
        """Constructor.
        
        Arguments:
            - commands: a list of Command objects
        """
        assert isinstance(commands, list)
        self.start = None
        self.end = None

        if len(commands) == 0:
            self.start = False # note that we are an empty list
            self.end = False
        else:
            # Convert the incoming list into a single-linked list
            prev_command = None
            for command_org in commands:
                command = command_org.clone() # clone to avoid clashes on the pointers
                if self.start is None:
                    self.start = command
                if prev_command is not None:
                    prev_command.next = command
                prev_command = command


    def clone(self):
        """Return a clone"""
        return CSequence([c.clone() for c in self.forward()])
    

    def add_backlinks(self):
        """Convert a single-linked list to a double-linked list"""
        prev_command = None
        for command in self.forward():
            command.prev = prev_command
            prev_command = command
        self.end = prev_command
        return self


    def forward(self, forever=False):
        """Iterate over the commands.
        
        Arguments:
            - forever: If True, keep returning None after the list is exhausted
        """
        command = self.start
        while command:
            yield command
            command = command.next
        if forever:
            while True:
                yield None


    def backward(self):
        """Iterate over the commands backwards"""
        assert self.end is not None # ensure we have converted the list to double-linked
        command = self.end
        while command:
            yield command
            command = command.prev
        
    
    def as_string(self):
        """Return a string representation of the object"""
        return '.'.join([c.as_string() for c in self.forward()])
    
    
    def equals(self, other):
        """Whether the two sequences are equal"""
        for a, b in zip(self.forward(forever=True), other.forward(forever=True)):
            if a is None and b is None:
                return True
            if a is None or b is None:
                return False
            if not a.equals(b):
                return False
        return True
    
    
    def order_by_node(self):
        """Return another sequence in which the commands are ordered by node; on equivalent nodes the original ordering is kept"""
        commands = [] # This implementation of heap_sort expects a list
        for i, command in enumerate(self.forward()):
            command.order = i
            commands.append(command)
        def compare(a, b):
            r = b.node.comp(a.node)
            if r != 0: return r
            if a.order == b.order: return 0
            if a.order < b.order: return 1
            return -1
        heap_sort(commands, compare)
        return CSequence(commands)


    def add_up_pointers(self):
        """Use on a lexicographically sorted sequence to add the up pointers to its commands"""
        prev_command = None
        for command in self.forward():
            if prev_command is None:
                command.up = None
            else:
                up = prev_command
                while True:
                    if up is None or up.node.is_ancestor_of(command.node):
                        command.up = up
                        break
                    up = command.up
            prev_command = command
        return self
        

    @classmethod
    def from_set(cls, cset):
        """Turn a command set into a command sequence; the order of commands is not guaranteed

        Arguments:
            - cset: A CSet object
        """
        return CSequence(list(cset.commands))
    
    
    @classmethod
    def order_set(cls, cset):
        """Order a command set to honour command ordering, and return a sequence.

        Arguments:
            - cset: A CSet object
        """
        sequence = CSequence(list(cset.commands)).order_by_node().add_backlinks()
        out = []
        for command in sequence.forward():
            if command.is_constructor():
                out.append(command)
        for command in sequence.backward():
            if not command.is_constructor():
                out.append(command)
        return CSequence(out)
    

    @classmethod
    def is_set_canonical(cls, cset):
        """Check whether a set of commands is canonical. This algorithm, apart from the ordering, is linear in the size of the set
        
        Arguments:
            - cset: A CSet object
        """
        sequence = cls.from_set(cset).order_by_node().add_up_pointers()
        
        prev_node = None
        for command in sequence.forward():
            if prev_node is not None and prev_node.equals(command.node):
                # Not canonical as multiple commands on the same node
                return False
            prev_node = command.node
            
            if command.up is not None and not (command.up.is_constructor_pair_with_next(command) or command.is_destructor_pair_with_next(command.up)):
                # Not canonical because closest command on an ancestor is not on a parent or they do not form a valid pair
                return False

        return True

    
    def get_canonical_set(self, checks=False):
        """Return the canonical command set extending this sequence.
        
        Arguments:
            - checks: If True, perform some checks to discover if the sequence is breaking
        """
        out = set()
        prev_command = None
        repl_before = None
        
        for command in self.order_by_node().forward():
            if prev_command is None:
                prev_command = command
                repl_before = command.before
                continue
            
            if command.node.equals(prev_command.node):
                
                if checks and not prev_command.after.equals(command.before):
                    raise Exception("Input sequence is breaking: input/output value mismatch")
                
            else:
                
                replacement = Command(prev_command.node, repl_before, prev_command.after)
                if not replacement.is_null():
                    out.add(replacement)
                repl_before = command.before

            prev_command = command
            
        if prev_command is not None:

            replacement = Command(prev_command.node, repl_before, prev_command.after)
            if not replacement.is_null():
                out.add(replacement)

        out = CSet(out)
        # If self is non-breaking, it is guaranteed that out is a canonical set.
        if checks and not self.__class__.is_set_canonical(out):
            raise Exception("Input sequence is breaking #2")
            
        return out
    
    
if __name__ == '__main__':
    
    # Test code
    n1 = Node(['d1'])
    n2 = Node(['d1', 'd2'])
    n3 = Node(['d1', 'd2', 'f3'])
    
    ve = Value(Value.T_EMPTY, 'e')
    vd = Value(Value.T_DIR, 'd')
    vf1 = Value(Value.T_FILE, 'f1')
    vf2 = Value(Value.T_FILE, 'f2')
    
    c1ed = Command(n1, ve, vd)
    c2ed = Command(n2, ve, vd)
    c3ef1 = Command(n3, ve, vf1)
    c3ef2 = Command(n3, ve, vf2)
    c3ff2 = Command(n3, vf1, vf2)
    
    s =  CSequence([c1ed, c2ed, c3ef1, c3ff2])
    s2 = CSequence([c3ef1, c2ed, c1ed, c3ff2])
    sc = CSequence([c1ed, c2ed, c3ef2]) # canonical
    
    # Test equals
    assert s.clone().equals(s.clone())
    assert not sc.clone().equals(s.clone())
    # Test order_by_node
    assert s2.clone().order_by_node().equals(s.clone())
    # Test get_canonical_set
    assert CSequence.from_set(s.clone().get_canonical_set()).order_by_node().equals(sc.clone())
    # Test is_set_canonical
    assert CSequence.is_set_canonical(CSet({c1ed.clone(), c2ed.clone(), c3ef1.clone()}))
    assert not CSequence.is_set_canonical(CSet({c3ef1.clone(), c3ff2.clone()}))
    assert not CSequence.is_set_canonical(CSet({c1ed.clone(), c3ef1.clone()}))
    # Test order_set
    assert CSequence.order_set(CSet({c3ff2.clone(), c2ed.clone(), c1ed.clone(), c3ef1.clone()})).equals(s.clone())

    print("Tests done")
    
