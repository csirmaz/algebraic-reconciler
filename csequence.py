
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
    def from_set_union(cls, command_sets, return_length=False):
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
    
        if return_length:
            return (CSequence(union), len(union))
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
        
        # from_set_union() applies order_by_node_value()
        union = cls.from_set_union(command_sets).add_up_pointers()
        
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


    @classmethod
    def get_any_merger(cls, command_sets, decisions=None, debug=False, return_lengths=False):
        """Given a set of jointly refluent canonical command sets, generate a merger.
        Suitable to produce all possible mergers; see Session.get_all_mergers().

        Arguments:
            - command_sets: A list or set of CSet objects or CSequence objects
            - decisions: Optional; a list of decisions a previous run of get_any_merger() returned
            - debug: {bool} Whether to print debug information
            
        Returns:
            (list of decisions, merger) or (None, None) if no more mergers can be generated
        """
        
        # The logic around storing decisions is not part of the algorithm, but makes it possible to generate all mergers
        # in a deterministic fashion
        
        if debug: print("---- get_any_merger starts ----")
        
        # First increment the decisions in the decisions list
        if decisions is None:
            decisions = []
        else:
            for i in reversed(range(len(decisions))):
                dec = decisions[i]
                if dec['current_decision'] < dec['num_options'] - 1:
                    dec['current_decision'] += 1
                    break
                if i == 0:
                    # No more mergers to generate
                    return (None, None)
                decisions.pop(i)
        
        decision_index = 0
        def make_decision(commands):
            """Choose a command from a list of commands.
            Retrieve the decision to be made from the decisions list or populate it.
            Note that decisions are purely identified by the order in which they are requested.
            """
            nonlocal decision_index
            if len(decisions) <= decision_index:
                assert len(decisions) == decision_index
                decisions.append({'current_decision': 0, 'num_options': len(commands), 'comment': " vs ".join([c.as_string() for c in commands])})
                decision_index += 1
                return commands[0]
            
            assert decisions[decision_index]['num_options'] == len(commands)
            d = decisions[decision_index]['current_decision']
            decision_index += 1
            return commands[d]
        
        def show_flags(commands):
            """For debugging; show the flags set on nodes"""
            print("Flags set")
            prev_command = None
            for command in commands.forward():
                if prev_command is None or not prev_command.node.equals(command.node):
                    print(f"  {command.node.as_string():<40}  "
                     + (" +dd" if command.node.has_destructor_on_dir else "    ")
                     + (" +ce" if command.node.has_constructor_on_empty_child else "    ")
                     + (" des^" if command.node.delete_destructors_up else "     ")
                     + (" cre*" if command.node.delete_creators_down else "     ")
                     + (" cre!" if command.node.delete_creators_strictly_down else "     ")
                    )
                prev_command = command
        
        # The algorithm proper starts here

        def process_flags(command):
            """Process flags around the current command and mark the command for deletion if needed"""
            if command.up and command.up.node.delete_creators_strictly_down:
                if debug and not command.node.delete_creators_down: print(f"Carry the delete_creators_strictly_down flag from {command.up.as_string()} to delete_creators_down on {command.as_string()}")
                command.node.delete_creators_down = True
                
            if command.up and command.up.node.delete_creators_down:
                if debug and not command.node.delete_creators_down: print(f"Carry the delete_creators_down flag from {command.up.as_string()} to {command.as_string()}")
                command.node.delete_creators_down = True
            
            # delete_creators_down marks commands for deletion whose output is not empty,
            # that is, constructors, edits and D>F destructors
            if command.node.delete_creators_down and (not command.after.is_empty()):
                if debug and not command.delete: print(f"Due to delete_creators_down, mark {command.as_string()} to be deleted")
                command.delete = True
                
            if command.node.delete_destructors_up and command.is_destructor():
                if debug and not command.delete: print(f"Due to delete_destructors_up, mark {command.as_string()} to be deleted")
                command.delete = True

        def mark_delete_destructors_up(command):
            """Mark the node of this command and all nodes above with delete_destructors_up"""
            if debug: print(f"Mark {command.as_string()} and ancestors with delete_destructors_up")
            while True:
                if command.node.delete_destructors_up:
                    break
                command.node.delete_destructors_up = True
                # We action adding the delete_destructors_up flag by unsetting has_destructor_on_dir
                command.node.has_destructor_on_dir = False
                if command.up:
                    command = command.up
                    continue
                break            
        
        # from_set_union() applies order_by_node_value()
        if return_lengths:
            union, len_union = cls.from_set_union(command_sets, return_length=True)
        else:
            union = cls.from_set_union(command_sets)
        union = union.add_up_pointers().add_backlinks()
        
        # (0) Initialise flags in top-down order
        for command in union.forward():
            command.delete = False
            node = command.node
            if node.has_destructor_on_dir is None: # has not been initialised
                node.has_destructor_on_dir = False
                node.has_constructor_on_empty_child = False
                node.delete_creators_down = False
                node.delete_creators_strictly_down = False
                node.delete_destructors_up = False
            if command.is_destructor() and command.before.is_dir():
                node.has_destructor_on_dir = True
            if command.up and command.is_constructor() and command.before.is_empty():
                command.up.node.has_constructor_on_empty_child = True

        # (1) First pass processing multiple commands on the same file node
        if debug: print("Pass 1 (file nodes)")

        def process_node_commands_1(commands):
            """Process a list of commands on the same node during the 1st pass"""
            if len(commands) == 1:
                return
            # If we have multiple commands (they are different as the union uniquifies), we have a conflict
            # Check for commands on a file
            # Because the input sets are refluent, the before (input) value of all commands here is the same
            if commands[0].before.is_file():
                # Decide which command to keep now - we may have a destructor <n,F,E>, constructor <n,F,D> or a number of edits <n,F,F?>
                keep = make_decision(commands)
                if debug: print(f"Found multiple commands on a file, keeping {keep.as_string()}")
                if keep.is_destructor(): # must be <n,F,E>
                    keep.node.delete_creators_strictly_down = True
                    if debug: print(f"Mark {keep.node.as_string()} with delete_creators_down")
                    # We don't need to action this flag now (e.g. mark commands as deleted) as file nodes are on incomparable paths
                elif keep.is_constructor(): # must be <n,F,D>
                    mark_delete_destructors_up(keep)
                else: # edit, <n,F,F>
                    mark_delete_destructors_up(keep)
                    keep.node.delete_creators_strictly_down = True # don't delete the current command though
                    if debug: print(f"Mark {keep.node.as_string()} with delete_creators_strictly_down")
                    # We don't need to action this flag now (e.g. mark commands as deleted) as file nodes are on incomparable paths
                # Mark other commands on this node for deletion
                for command in commands:
                    if not command.equals(keep):
                        command.delete = True
                        
        prev_command = None
        node_commands = None
        for command in union.forward():
            # Processing flags is actually not needed here because file nodes are on incomparable paths
            process_flags(command)
            if command.delete:
                continue

            if prev_command and prev_command.node.equals(command.node):
                node_commands.append(command)
            else:
                if node_commands:
                    process_node_commands_1(node_commands)                
                node_commands = [command]
            prev_command = command
            
        if node_commands:
            process_node_commands_1(node_commands)    

        # (2) Second pass processing <^n,D,FE>,<n,E,DF> command pairs (bottom-up)
        if debug: print("Pass 2 (command pairs)")

        prev_command = None
        for command in union.backward():
            process_flags(command)
            if command.delete:
                continue

            # Only execute the below once on every node
            if prev_command is None or not prev_command.node.equals(command.node):
                # Note that command.up.node.has_destructor_on_dir also reflects deletions
                if command.node.has_destructor_on_dir and command.node.has_constructor_on_empty_child:
                    # Decide whether to keep the parent or the children
                    # Use a dummy command to represent children
                    dummy = Command(Node(['_children']), Value(Value.T_EMPTY, ''), Value(Value.T_DIR, ''))
                    keep = make_decision([command, dummy])
                    if debug: print(f"Found destructor-constructor conflict on {command.as_string()}; keeping {keep.as_string()}")
                    if keep.equals(command): # keep the destructors on the parent
                        command.node.delete_creators_strictly_down = True
                        if debug: print(f"Mark {command.node.as_string()} with delete_creators_down")
                        # We don't need to action this flag now because deleting constructors
                        # on empty children and below are independent of other conflicts of this type;
                        # and deleting <*,D,F> (a creator but also potentially a parent in this type of conflict)
                        # in previously processed conflicts can be done. They must have a <*,D,E> on the parent
                        # which will be the winner.
                    else: # keep constructors on the children
                        mark_delete_destructors_up(command)
            prev_command = command
                    
        # (3) Conflicts on empty nodes (top-down)
        if debug: print("Pass 3 (empty nodes)")

        def process_node_commands_3(commands):
            """Process a list of commands on the same node during the 3rd pass"""
            if len(commands) == 1:
                return
            # If we have multiple commands (they are different as the union uniquifies), we have a conflict
            # Because the input sets are refluent, the before (input) value of all commands here is the same
            if commands[0].before.is_empty():
                # Decide which command to keep - we may have constructors <n,E,F?> or <n,E,D>
                keep = make_decision(commands)
                if debug: print(f"Found multiple commands on empty value, keeping {keep.as_string()}")
                if keep.after.is_file(): # we cannot have non-empty values below
                    keep.node.delete_creators_strictly_down = True # don't delete the current command though
                    if debug: print(f"Mark {keep.as_string()} with delete_creators_strictly_down")
                    # We don't need to action this flag now (e.g. mark commands as deleted) as we're in a top-down pass
                # Mark other commands on this node for deletion
                for command in commands:
                    if not command.equals(keep):
                        command.delete = True

        prev_command = None
        node_commands = None
        for command in union.forward():
            process_flags(command)
            if command.delete:
                continue

            if prev_command and prev_command.node.equals(command.node):
                node_commands.append(command)
            else:
                if node_commands:
                    process_node_commands_3(node_commands)
                node_commands = [command]
            prev_command = command
            
        if node_commands:
            process_node_commands_3(node_commands)
        
        # (4) Conflicts on directory nodes (bottom-up)
        if debug: print("Pass 4 (directory nodes)")

        def process_node_commands_4(commands):
            """Process a list of commands on the same node during the 4th pass"""
            if len(commands) == 1:
                return
            # If we have multiple commands (they are different as the union uniquifies), we have a conflict
            # Because the input sets are refluent, the before (input) value of all commands here is the same
            if commands[0].before.is_dir():
                # Decide which command to keep - we may have destructors D>F? and D>E
                keep = make_decision(commands)
                if debug: print(f"Found multiple commands on directory, keeping {keep.as_string()}")
                if keep.after.is_file(): # we cannot destruct directories above
                    if keep.up:
                        mark_delete_destructors_up(keep.up)
                # Mark other commands on this node for deletion
                for command in commands:
                    if not command.equals(keep):
                        command.delete = True

        prev_command = None
        node_commands = None
        for command in union.backward():
            process_flags(command)
            if command.delete:
                continue

            if prev_command and prev_command.node.equals(command.node):
                node_commands.append(command)
            else:
                if node_commands:
                    process_node_commands_4(node_commands)
                node_commands = [command]
            prev_command = command
            
        if node_commands:
            process_node_commands_4(node_commands)
        
        # (5) Finally, collect the remaining commands
        merger = []
        for command in union.forward():
            process_flags(command)
            if command.delete:
                continue
            merger.append(command)
        
        if debug:
            show_flags(union)
            # Display the decisions
            print("Decisions made")
            for i, d in enumerate(decisions):
                print(f"  #{i} {d['current_decision']} of {d['num_options']} for {d['comment']}")
        
        if return_lengths:
            return (decisions, CSequence(merger), {'union': len_union, 'merger': len(merger)})
        return (decisions, CSequence(merger))
