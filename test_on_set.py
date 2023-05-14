
# This script measures the time it takes to create a merger on synthetic data sets

from timeit import default_timer as timer
import gc
import random
import time

from command import Command
from node import Node
from value import Value
from csequence import CSequence
from heapsort import heap_sort


class Test:
    """Create a set of command sequences applied to the filesystem where
    - at the paths "i" there are directories
    - at the paths "i/j" there are directories
    - at the paths "i/j/k" there are files
    where
    - 0 <= i < size
    - 0 <= j < size
    - 0 <= k < size
    - (i,j) and (j,k) are not farther from each other than `spread` modulo `size`
    
    There is a command sequence associated with each user/replica.
    User `u` has the following commands:
    - Delete the files at i/u/k (*/u/*)
    - Delete the directories at i/u (*/u)
    - For x in (user-1, user, user+1) modulo `size`:
        - Change files to directories at i/j'/x where j' != u
        - Create files at i/j'/x/l with unique content where j' != u and 0<l<=size
    """
    
    def __init__(self, size, spread, num_users):
        self.size = size
        self.spread = spread
        self.num_nodes = 0
        self.nodes = {}
        self.unique_content = 0
        self.sequence_length = None
        self.sequences = []
        self.generate_sequences(num_users)

    def is_valid_path(self, path):
        for i in range(min(len(path), 3) - 1): # The 4th level can spread out more
            d = path[i] - path[i+1]
            d = d % size
            if not(d <= self.spread or d >= self.size - self.spread):
                return False
        return True

    def get_node(self, path):
        """Return a unique node object for the path"""
        n = self.nodes
        for p in path:
            assert p != '_node_' # This is used to store the node objects
            if p not in n:
                n[p] = {}
            n = n[p]
        if '_node_' not in n:
            n['_node_'] = Node([str(p) for p in path])
            # print(f"New node {num_nodes} {path}")
            self.num_nodes += 1
        return n['_node_']

    def get_unique_content(self):
        self.unique_content += 1
        return f"::{self.unique_content}"

    def get_org_value(self, path):
        """Get the original Value at path in the filesystem"""
        if len(path) < 3:
            return Value(Value.T_DIR, '')
        if len(path) == 3:
            return Value(Value.T_FILE, ":".join([str(p) for p in path]))
        return Value(Value.T_EMPTY, '')

    def cmd(self, path, new_value):
        """Convenience function to create a command"""
        if new_value == 'E':
            new_value = Value(Value.T_EMPTY, '')
        elif new_value == 'D':
            new_value = Value(Value.T_DIR, '')
        else:
            new_value = Value(Value.T_FILE, new_value)
        return Command(self.get_node(path), self.get_org_value(path), new_value)

    def generte_user_commands(self, user):        
        assert user >= 0 and user < self.size
        commands = []
        for i in range(self.size):
            for k in range(self.size):
                path = [i, user, (user + k) % self.size]
                if not self.is_valid_path(path): continue
                commands.append(self.cmd(path, 'E'))
            path = [i, user]
            if not self.is_valid_path(path): continue
            commands.append(self.cmd(path, 'E'))
        # print(f"  User {user} commands after stage 1: {len(commands)}")

        if True:
            for i in range(self.size):
                for j in range(self.size):
                    if j == user: continue
                    for x in (-1, 0, 1):
                        k = ((user + x) % size)
                        path = [i, j, k]
                        if not self.is_valid_path(path): continue
                        commands.append(self.cmd(path, 'D'))
                        for l in range(self.size):
                            path = [i, j, k, l]
                            commands.append(self.cmd(path, self.get_unique_content()))

        if self.sequence_length is None:
            self.sequence_length = len(commands)
        assert self.sequence_length == len(commands)
        return CSequence(commands, clone=False)


    def generate_sequences(self, num_users):
        self.sequences = []
        for i in range(num_users):
            self.sequences.append(self.generte_user_commands(i))


settings = []
for spread in range(1, 6):
    for size in range(5, 15):
        if 2*spread+1 > size: continue
        for num_users in range(2, size): # number of users
            for num_mergers in [1, 3]: # Get this many mergers
                settings.append({
                    'spread': spread,
                    'size': size,
                    'num_users': num_users,
                    'num_mergers': num_mergers
                })


num_experiments = 10

# CSV header
csv_hdr = ([
    'spread', 'size', 'num_users', 'num_mergers', 'max_nodes', 'num_nodes', 'seq_len', 'union_len', 'merger_len', 
    'avg_time', 'mse', 'merger_time', 'command_time'
    ] + [f"t{i}" for i in range(num_experiments)])
print(",".join(csv_hdr))

experiments = {}
for experiment in range(num_experiments):
    random.shuffle(settings)
    for set_ix, setting in enumerate(settings):
        spread = setting['spread']
        size = setting['size']
        num_users = setting['num_users']
        num_mergers = setting['num_mergers']

        max_nodes = size*(2*spread+1) + size*(2*spread+1)*(2*spread+1) + size*(2*spread+1)*(2*spread+1)*size
                
        if False and experiment == 0:
            test1 = Test(size=size, spread=spread, num_users=num_users)
            for s in test1.sequences:
                assert CSequence.is_set_canonical(s.as_set())
    
            test2 = Test(size=size, spread=spread, num_users=num_users)
            assert CSequence.check_refluent(test2.sequences)
                    
        decisions = None
        i = 0
        time_spent = 0
        while True:
            test = Test(size=size, spread=spread, num_users=num_users) # reset flags, etc.
            gc.collect()
            start = timer()
            decisions, merger, lengths = CSequence.get_any_merger(test.sequences, decisions=decisions, debug=False, return_lengths=True)
            end = timer()
            time_spent += end - start
            if decisions is None: # no more mergers
                break
            i += 1
            if i >= num_mergers:
                break
            
        if i == num_mergers: # We have enough mergers
            exp_data = [spread, size, num_users, num_mergers, max_nodes, test.num_nodes, test.sequence_length, lengths['union'], lengths['merger']]
            key = ":".join([str(x) for x in exp_data])
            if key not in experiments:
                experiments[key] = {'data': exp_data, 'times':[]}
            print(f"PROGRESS {(experiment*len(settings)+set_ix)/(num_experiments*len(settings))*100}%")
            experiments[key]['times'].append(time_spent)

    if experiment < num_experiments - 1:
        time.sleep(30)

# CSV lines
import numpy as np
for k, exp_data in experiments.items():
    times = np.array(exp_data['times'])
    avg = np.average(times)
    mse = np.sum(np.square(times - avg))
    csv = exp_data['data'] + [avg, mse, avg/exp_data['data'][3], avg/exp_data['data'][3]/exp_data['data'][7]] + exp_data['times']
    print(",".join([str(x) for x in csv]))
