
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
    
    def __init__(self, commands, clone=True):
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
                if clone:
                    command = command_org.clone() # clone to avoid clashes on the pointers
                else:
                    command = command_org
                command.prev = None
                if self.start is None:
                    self.start = command
                if prev_command is not None:
                    prev_command.next = command
                prev_command = command
            prev_command.next = None


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
        
    
    def as_string(self, with_up=False):
        """Return a string representation of the object
        
        Arguments:
            - with_up: {bool} Display information about the up pointers
        """
        if with_up:
            return "\n".join([
                    f"{id(c)}{c.as_string()}^{'x' if c.up is None else id(c.up)}"
                for c in self.forward()])                
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


    def order_by_node_value(self):
        """Return another sequence in which the commands are ordered by node and value. Equivalent commands are guaranteed to be next to each other"""
        commands = list(self.forward()) # This implementation of heap_sort expects a list
        def compare(a, b):
            r = b.node.comp(a.node)
            if r != 0: return r
            r = b.before.comp(a.before)
            if r != 0: return r
            return b.after.comp(a.after)
        heap_sort(commands, compare)
        return CSequence(commands)


    def add_up_pointers(self):
        """Use on a lexicographically sorted sequence to add the up pointers to its commands.
        Note that in this implementation the pointers are between commands, not nodes.
        """
        prev_command = None
        for command in self.forward():
            if prev_command is None:
                command.up = None
            else:
                up_command = prev_command
                while True:
                    if up_command is None or up_command.node.is_ancestor_of(command.node):
                        command.up = up_command
                        break
                    up_command = up_command.up
            prev_command = command
        return self
        

    @classmethod
    def from_set(cls, cset):
        """Turn a command set into a command sequence; the order of commands is not guaranteed

        Arguments:
            - cset: A CSet object
        """
        return CSequence(list(cset.commands))


    def as_set(self):
        """Return a set containing the commands of this sequence"""
        return CSet({command for command in self.forward()})
        

    @classmethod
    def from_set_union(cls, command_sets):
        """Turn the union of some command sets into a command sequence; the order of commands is not guaranteed

        Arguments:
            - command_sets: A list or set of CSet objects or CSequence objects
        """
        # Create the union of the command sets by ordering all commands and filtering out the equal ones
        all = []
        for cset in command_sets:
            if isinstance(cset, CSet):
                all.extend(list(cset.commands))
            elif isinstance(cset, CSequence):
                all.extend([c for c in cset.forward()])
            else:
                raise Exception("Unknown object received")

        union = []
        prev_command = None
        for command in CSequence(all).order_by_node_value().forward():
            if prev_command is None or (not command.equals(prev_command)):
                union.append(command)
            prev_command = command
        return CSequence(union)

    
    @classmethod
    def order_set(cls, cset):
        """Order a canonical command set to honour command ordering, and return a sequence.

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
        """Return the canonical command set that is the semantic extension of this sequence.
        
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
    
    
    @classmethod
    def get_greedy_merger(cls, command_sets, debug=False):
        """Given a set of jointly refluent canonical command sets, generate a merger.

        Arguments:
            - command_sets: A list or set of CSet objects or CSequence objects
            - debug: {bool} Whether to print debug information
        """
        
        union = cls.from_set_union(command_sets).order_by_node().add_up_pointers()
        
        if debug: 
            for cset in command_sets:
                print(f"Input: {cset.as_string()}")
            print(f"Union (ordered): {union.as_string()}")

        # for completeness only
        for command in union.forward():
            command.node.delete_conflicts_down = False
        
        merger = []
        delete_on_node = None
        for command in union.forward():
            if debug: print(f"Current command: {command.as_string()}   Del_node: {'None' if delete_on_node is None else delete_on_node.as_string()}   Up: {'None' if command.up is None else command.up.as_string()}")
            if delete_on_node is not None and command.node.equals(delete_on_node):
                if debug: print("Deleted by node")
                continue
            
            # Note: delete_conflicts_down is set on the Node object so we would find it even if the up pointer points
            # to another command on the same node. This relies on the fact that each path is represented by a single
            # Node object only, guaranteed by the Session.
            
            if command.up is not None and command.up.node.delete_conflicts_down:
                if debug: print("Carrying down delete_conflicts_down")
                command.node.delete_conflicts_down = True
                if not command.after.is_empty():
                    # delete_conflicts_down is only set if a command on an ancestor node creates a non-directory value
                    # and so we are in conflict by the weak definition
                    if debug: print("Deleted by delete_conflicts_down")
                    continue
            
            # We are not in conflict, and so "final"
            if debug: print("Command is final")
            merger.append(command)
            delete_on_node = command.node
            if not command.after.is_dir():
                # By the weak definition we will be in conflict with descendants creating a non-empty value
                if debug: print("Marking with delete_conflicts_down")
                command.node.delete_conflicts_down = True
                
        if debug: print(f"Merger: {CSequence(merger).as_string()}")
        return CSequence(merger)
    
    
    @classmethod
    def check_refluent(cls, command_sets, debug=False):
        """Given a set of canonical command sets, determine if they are jointly refluent.
        
        Arguments:
            - command_sets: A list or set of CSet objects or CSequence objects
            - debug: {bool} Whether to print debug information
        """

        # Fill in the index bitmaps
        def set_bit(node, bit):
            v = 1 << bit
            if node.index is None:
                node.index = v
            else:
                node.index |= v
        
        for i, cset in enumerate(command_sets):
            if isinstance(cset, CSet):
                for command in cset.commands:
                    set_bit(command.node, i)
            elif isinstance(cset, CSequence):
                for command in cset.forward():
                    set_bit(command.node, i)
            else:
                raise Exception("Unknown object received")
            
        union = cls.from_set_union(command_sets).order_by_node().add_up_pointers()
        if debug: print(union.as_string(with_up=True))
       
        prev_command = None
        for command in union.forward():
            
            if prev_command is not None and prev_command.node.equals(command.node):
                # Condition a)
                if not prev_command.before.equals(command.before):  
                    if debug: print(f"Commands {command.as_string()} and {prev_command.as_string()} have different input values")
                    return False
                
            if command.up is not None:
                
                # Condition b)
                # - if we have m above n so that there's a command on both, then the "up" pointer is filled in
                #   for commands on n
                # - if as we require, there are commands on the parent of n, then the up pointers must point there
                if not command.up.node.is_parent_of(command.node):
                    if debug: print(f"Up pointer at {command.as_string()} does not point to a parent")
                    return False
                
                # Condition c)
                # - command.up is always filled in if there's a command above us
                # - command.up is on the parent node if there's a command on the parent node
                # - if no "up" points to a given node, we're not checking it, but that is fine
                #   as the index needs to be a subset on descendants and the index is empty on the descendants
                # - we know all input (before) values match, so it's enough to check one command
                if command.up.node.is_parent_of(command.node) and not command.up.before.is_dir():
                    if (command.node.index & command.up.node.index) != command.node.index:
                        if debug: print(f"Index at {command.as_string()}: {command.node.index} not a subset of index at {command.up.as_string()}: {command.up.node.index}")
                        return False
                
            # Condition d)
            if not command.before.is_empty():
                if not (
                    command.up is None # no commands above us so index set empty
                    or
                    (command.up.node.index & command.node.index) == command.up.node.index
                ):
                    if debug: print(f"Index at {command.as_string()}: {command.node.index} not a superset of index at {command.up.as_string()}: {command.up.node.index}")
                    return False
        
            prev_command = command

        return True
