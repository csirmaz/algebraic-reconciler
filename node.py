
class Node:
    """Class representing a filesystem node

    Properties:
        - path: a list of strings
        - delete_conflicts_down: an optional Boolean flag used during constructing a merger
        - index: an optional bitmap
        - has_destructor_on_dir: optional bool flag used by get_any_merger(): whether there is a destructor command on a directory value on this node
        - has_constructor_on_empty_child: optional bool flag used by get_any_merger(): whether there is a constructor command on an empty value on a child noe
        - delete_creators_strictly_down: optional bool flag used by get_any_merger(): whether to discard commands with non-empty output below this node
        - delete_creators_down: optional bool flag used by get_any_merger(): whether to discard commands with non-empty output on this node and below
        - delete_destructors_up: optional bool flag used by get_any_merger(): whether to discard destructors on this node (and above)

    Usage:
        paths are lists of names (strings), e.g.
        n = Node(['dir1', 'dir2', 'filename'])
    """
    
    def __init__(self, path):
        """Constructor
        
        Arguments:
            - path: a list of strings, e.g. ['dir1', 'dir2', 'filename']
        """
        assert isinstance(path, list)
        self.path = path
        self.delete_conflicts_down = None
        self.index = None
        self.has_destructor_on_dir = None
        self.has_constructor_on_empty_child = None
        self.delete_creators_strictly_down = None
        self.delete_creators_down = None
        self.delete_destructors_up = None


    def as_string(self):
        """Return a string representation of the object"""
        return '/'.join(self.path)

    
    def equals(self, other):
        """Whether the curent object is equal to another Node object
        
        Arguments:
            - other: a Node object
        """
        return (self.comp(other) == 0)

    
    def is_ancestor_of(self, other):
        """Whether the current object is an ancestor of another Node object"""
        if len(self.path) >= len(other.path):
            return False
        return (self.path == other.path[0:len(self.path)])

    
    def is_descendant_of(self, other):
        """Whether the current object is a descendand of another Node object"""
        return other.is_ancestor_of(self)

    
    def is_parent_of(self, other):
        """Whether the current object is the parent of another Node object"""
        return (self.path == other.path[0:-1])

    
    def get_parent(self):
        """Get an object representing the parent of the current object"""
        return Node(self.path[0:-1])


    def comp(self, other):
        """Comparison function (returning -1,0,1) following lexicographic order"""
        if self.path == other.path:
            return 0
        if self.path < other.path:
            return -1
        return 1

            
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

