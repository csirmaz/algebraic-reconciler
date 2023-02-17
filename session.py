
from command import Command
from node import Node
from value import Value
from csequence import CSequence
from heapsort import heap_sort

class Session:
    
    """A Session is used to process command and command sequence specifications.
    It also contains a subset of the underlying filesystem nodes, and ensures that
    each path is represented by a unique Node object."""
    
    def __init__(self, spec, use_list=False, debug=False):
        """Process one or more command sequences represented as strings, simulating
        processing incoming synchronization requests.
        
        Format:
        a=<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
        b=<d1|D|E>
        
        where
        ; separates sequence definitions
        = separates the name of a sequence (becomes a property of the session)
        . separates commands in a sequence
        | separates the path and values in a command
        / separates parts of a path
        the first character of a value denotes its type (E,F,D)
        
        Arguments:
            - spec: {string} session spec in the format above
            - use_list: {bool} whether to collect the sequences in a list instead of setting them as properties
            - debug: {bool} whether to print debug information
        """
        value_type = {
            'E': Value.T_EMPTY,
            'F': Value.T_FILE,
            'D': Value.T_DIR
        }
        sequences = []
        all_commands = []
        for sequence_label_spec in spec.split(';'):
            label, sequence_spec = sequence_label_spec.split('=')
            commands = []
            for command_spec in sequence_spec.strip().split('.'):
                command_spec = command_spec.strip().strip('<>').split('|')
                node = Node(command_spec[0].strip().split('/'))
                command_spec[1] = command_spec[1].strip()
                before = Value(value_type[command_spec[1][0]], command_spec[1][1:])
                command_spec[2] = command_spec[2].strip()
                after = Value(value_type[command_spec[2][0]], command_spec[2][1:])
                command = Command(node, before, after)
                all_commands.append(command)
                commands.append(command)
            if debug: print(f"Creating {label.strip()}")
            seq = CSequence(commands, clone=False) # important not to clone as we adjust the command objects below
            if use_list:
                sequences.append(seq)
            else:
                setattr(self, label.strip(), seq) 
            if debug: print(f"Creating DONE")
            
        if use_list:
            self.sequences = sequences
            
        # Process all commands to ensure that each path is represented by one Node object
        def compare(a, b):
            return b.node.comp(a.node)
        heap_sort(all_commands, compare)
        
        prev_node = None
        for command in all_commands:
            if debug: print(f"{command.as_string()} with {command.node}")
            if prev_node is not None and command.node.equals(prev_node):
                if debug: print(f"Replacing node {command} {command.node} -> {prev_node}")
                command.node = prev_node
            prev_node = command.node


def get_all_mergers(session_def, debug=False):
    """Check a set of sequences and produce all possible mergers"""
    
    s = Session(session_def, use_list=True)
    for seq in s.sequences:
        assert CSequence.is_set_canonical(seq.as_set())

    s = Session(session_def, use_list=True)
    assert CSequence.check_refluent(s.sequences)
    
    decisions = None
    while True:
        s = Session(session_def, use_list=True) # reset flags, etc.
        decisions, merger = CSequence.get_any_merger(s.sequences, decisions=decisions, debug=debug)
        if decisions is None:
            break
        print("Merger:")
        print(merger.as_string())
    

if __name__ == '__main__':
    
    # Test code

    # Test equals
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>""")
    assert s.a.equals(s.b)
    
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>;
                   c=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>""")
    assert not s.a.equals(s.c)
    
    # Test order_by_node
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>;
                   b=<d1/d2/f3|E|Ff1>.<d1/d2|E|D>.<d1/d2/f3|Ff1|Ff2>.<d1|E|D>""")
    assert s.b.order_by_node().equals(s.a)
    
    
    # Test get_canonical_set
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>;
                   c=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>""")
    assert CSequence.from_set(s.a.get_canonical_set()).order_by_node().equals(s.c)

    # Test is_set_canonical
    s = Session("a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>")
    assert CSequence.is_set_canonical(s.a.as_set())

    s = Session("a=<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>")
    assert not CSequence.is_set_canonical(s.a.as_set())

    s = Session("a=<d1|E|D>.<d1/d2/f3|E|Ff1>")
    assert not CSequence.is_set_canonical(s.a.as_set())

    # Test order_set
    s = Session("""a=<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1|E|D>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>""")
    assert CSequence.order_set(s.a.as_set()).equals(s.b)

    # Test from_set_union
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>;
                   t=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|E|Ff2>""")
    assert CSequence.from_set_union([s.a, s.b]).as_set().slow_equals(s.t.as_set())

    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2|E|Ff1>;
                   t=<d1|E|D>.<d1/d2|E|D>.<d1/d2|E|Ff1>.<d1/d2/f3|E|Ff1>""")
    assert CSequence.from_set_union([s.a, s.b]).as_set().slow_equals(s.t.as_set())
    
    # Test get_greedy_merger
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>;
                   t1=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   t2=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>""")
    merger = CSequence.get_greedy_merger([s.a, s.b]).as_set()
    assert merger.slow_equals(s.t1.as_set()) or merger.slow_equals(s.t2.as_set())
    
    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>;
                   t1=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   t2=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>""")
    merger = CSequence.get_greedy_merger([s.b, s.a]).as_set()
    assert merger.slow_equals(s.t1.as_set()) or merger.slow_equals(s.t2.as_set())

    s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   b=<d1|E|D>.<d1/d2|E|Ff1>;
                   t1=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
                   t2=<d1|E|D>.<d1/d2|E|Ff1>""")
    merger = CSequence.get_greedy_merger([s.a, s.b]).as_set()
    assert merger.slow_equals(s.t1.as_set()) or merger.slow_equals(s.t2.as_set())
    
    # Test check_refluent
    s = Session("""a=<1|D|Ff1>;
                   b=<1/2|E|Ff2>""")
    assert CSequence.check_refluent([s.a, s.b])
    
    s = Session("""a=<1|Ff1|Ff2>;
                   b=<1/2|E|Ff3>""")
    assert not CSequence.check_refluent([s.a, s.b])    

    s = Session("""a=<1/2|D|E>.<1|D|E>;
                   b=<1/2/3|E|D>;
                   c=<1/2|D|Ff2>.<0|E|D>;
                   d=<1/2/3|E|D>.<1/2/3/4|E|Ff3>;
                   e=<1/2/3|E|D>.<1/2/3/4b|E|Ff4>""")
    assert CSequence.check_refluent([s.a, s.b, s.c, s.d, s.e])

    s = Session("""a=<1/2|D|E>.<1|D|E>;
                   b=<1/2/3|E|D>;
                   c=<1/2|D|Ff2>.<0|E|D>;
                   d=<1/2/3|F|D>.<1/2/3/4|E|Ff3>;
                   e=<1/2/3|E|D>.<1/2/3/4b|E|Ff4>""")
    assert not CSequence.check_refluent([s.a, s.b, s.c, s.d, s.e]) # Wrong input value in s.d[0]

    s = Session("""a=<1/2|F|E>.<1|D|E>;
                   b=<1/2/3|E|D>;
                   c=<1/2|F|Ff2>.<0|E|D>;
                   d=<1/2/3|E|D>.<1/2/3/4|E|Ff3>;
                   e=<1/2/3|E|D>.<1/2/3/4b|E|Ff4>""")
    assert not CSequence.check_refluent([s.a, s.b, s.c, s.d, s.e]) # s.a, s.c assume F at 1/2; others assume D

    s = Session("""a=<1/2|D|E>.<1|D|E>;
                   b=<1/2/3/4/5/6|E|D>""")
    assert not CSequence.check_refluent([s.a, s.b])
    
    # Test get_all_mergers
    sessiondef = """a=<1/2/3|D|E>.<1/2|D|E>;
                    b=<1/2/3|D|E>.<1/2|D|Fa>;
                    c=<1/2/3/4|E|D>.<1/2/3/4/5|E|Fb>;
                    d=<1/2/3/4|E|D>.<1/2/3/4/5|E|D>.<1/2/3/4/5/6|E|D>;
                    e=<1/2/3/4b|E|Fc>;
                    f=<1/2/3/4c|E|D>;
                    g=<6/7/8|F|E>.<6/7|D|E>;
                    h=<6/7/8|F|Fd>;
                    i=<6/7/8|F|D>.<6/7/8/9|E|D>;
                    j=<6/7/8b|E|Fe>"""
    get_all_mergers(sessiondef, debug=True)
