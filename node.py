
class Node:
    """Class representing a filesystem node
    
    paths are lists of names (strings), e.g.
    n = Node(['dir1', 'dir2', 'filename'])
    """
    
    def __init__(self, path):
        self.path = path
        
    def as_string(self):
        return '/'.join(self.path)
    
    def equals(self, other):
        """Whether the curent object is equal to another object"""
        return (self.comp(other) == 0)
    
    def is_ancestor_of(self, other):
        """Whether the current object is an ancestor of the other object"""
        if len(self.path) >= len(other.path):
            return False
        return (self.path == other.path[0:len(self.path)])
    
    def is_descendant_of(self, other):
        """Whether the current object is a descendand of another object"""
        return other.is_ancestor_of(self)
    
    def is_parent_of(self, other):
        """Whether the current object is the parent of another object"""
        return (self.path == other.path[0:-1])
    
    def get_parent(self):
        """Get an object representing the parent of the current object"""
        return Node(self.path[0:-1])

    def comp(self, other):
        """Comparison function (returning -1,0,1) following lexicographic order"""
        # The </== operators between lists should do the same, but making the logic explicit here
        i = 0
        while True:
            if i >= len(self.path):
                if i >= len(other.path):
                    return 0
                return -1 # self.path is shorter and a prefix
            if i >= len(other.path):
                return 1 # other.path is shorter and a prefix
            if self.path[i] < other.path[i]:
                return -1
            if self.path[i] > other.path[i]:
                return 1
            i += 1
            
    def is_less(self, other):
        """Whether the current object is less than another following lexicographic order"""
        return (self.comp(other) == -1)
    
    def is_greater(self, other):
        """Whether the current object is greater than another following lexicographic order"""
        return (self.comp(other) == 1)

if __name__ == '__main__':
    
    # Test code
    assert Node(['a','b','c']).is_descendant_of(Node(['a']))
    assert not Node(['a','c']).is_descendant_of(Node(['x']))
    assert Node(['a','b','c']).equals(Node(['a','b','c','d']).get_parent())
    assert Node(['a','b','c']).is_less(Node(['a','c']))
    assert Node([]).is_parent_of(Node(['a']))
    print("Tests done")

        
