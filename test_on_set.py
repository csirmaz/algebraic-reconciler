
from command import Command
from node import Node
from value import Value
from csequence import CSequence
from heapsort import heap_sort


size = 9
spread = 2

def is_valid_path(path):
    for i in range(min(len(path), 3) - 1): # The 4th level can spread out more
        d = path[i] - path[i+1]
        d = d % size
        if not(d <= spread or d >= size - spread):
            return False
    return True

assert is_valid_path([0,0,1])
assert is_valid_path([0,size-1,size-1])
assert not is_valid_path([4, 0])

num_nodes = 0
nodes = {}
def get_node(path):
    """Return a unique node object for the path"""
    global num_nodes
    n = nodes
    for p in path:
        assert p != '_node_' # This is used to store the node objects
        if p not in n:
            n[p] = {}
        n = n[p]
    if '_node_' not in n:
        n['_node_'] = Node([str(p) for p in path])
        # print(f"New node {num_nodes} {path}")
        num_nodes += 1
    return n['_node_']


unique_content = 0
def get_unique_content():
    global unique_content
    unique_content += 1
    return f"::{unique_content}"


def get_org_value(path):
    """Get the original Value at path in the filesystem"""
    if len(path) < 3:
        return Value(Value.T_DIR, '')
    if len(path) == 3:
        return Value(Value.T_FILE, ":".join([str(p) for p in path]))
    return Value(Value.T_EMPTY, '')


def cmd(path, new_value):
    """Convenience function to create a command"""
    if new_value == 'E':
        new_value = Value(Value.T_EMPTY, '')
    elif new_value == 'D':
        new_value = Value(Value.T_DIR, '')
    else:
        new_value = Value(Value.T_FILE, new_value)
    return Command(get_node(path), get_org_value(path), new_value)

    
def generte_user_commands(user):
    # Delete all files at */user/*
    # Delete directories at */user

    # For x in (user-1, user, user+1):
    #   Edit files to directories at */(!=user)/x
    #   Create files at */(!=user)/x/* with unique content
    
    assert user >= 0 and user < size
    commands = []
    for i in range(size):
        for k in range(size):
            path = [i, user, (user + k) % size]
            if not is_valid_path(path): continue
            commands.append(cmd(path, 'E'))
        path = [i, user]
        if not is_valid_path(path): continue
        commands.append(cmd(path, 'E'))
    # print(f"  User {user} commands after stage 1: {len(commands)}")

    if True:
        for i in range(size):
            for j in range(size):
                if j == user: continue
                for x in (-1, 0, 1):
                    k = ((user + x) % size)
                    path = [i, j, k]
                    if not is_valid_path(path): continue
                    commands.append(cmd(path, 'D'))
                    for l in range(size):
                        path = [i, j, k, l]
                        commands.append(cmd(path, get_unique_content()))

    print(f"User {user} command sequence is {len(commands)} long")
    return CSequence(commands, clone=False)
    
print(f"Expected/max size of filesystem: {size*(2*spread+1) + size*(2*spread+1)*(2*spread+1) + size*(2*spread+1)*(2*spread+1)*size}")
for u in range(size):
    generte_user_commands(u).as_string()
print(f"Number of nodes set up: {num_nodes}")
