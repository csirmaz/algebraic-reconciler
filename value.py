

class Value:
    """Class representing a filesystem value
    
    v = Value(Value.T_FILE, 'f1')
    """
    
    # Constants describing the type of the value
    # There is an intrinsic ordering between the types
    # T_EMPTY < T_FILE < T_DIR
    # Note that this order will go from leaf nodes to roots
    T_EMPTY = 100
    T_FILE = 101
    T_DIR = 102


    def __init__(self, type_, contents):
        self.type_ = type_
        self.contents = contents

        
    def as_string(self):
        t = {
            self.T_EMPTY: 'E',
            self.T_FILE: 'F',
            self.T_DIR: 'D'
        }
        return f"{t[self.type_]}({self.contents})"
    
    
    def is_empty(self):
        """Whether the value is an empty value"""
        return (self.type_ == self.T_EMPTY)
    
    
    def is_file(self):
        """Whether the value is a file"""
        return (self.type_ == self.T_FILE)
    
    
    def is_dir(self):
        """Whether the value is a directory"""
        return (self.type_ == self.T_DIR)

    
    def type_eq(self, other):
        """Whether the current and another object are type-equal"""
        return (self.type_ == other.type_)

    
    def type_less(self, other):
        """Whether the current object is type-less than another object"""
        return (self.type_ < other.type_)


    def type_less_eq(self, other):
        """Whether the current object is type-less-or-equal than another object"""
        return (self.type_ <= other.type_)

    
    def type_greater(self, other):
        return (self.type_ > other.type_)

    
    def type_greater_eq(self, other):
        return (self.type_ >= other.type_)

    
    def equals(self, other):
        """Whether the current object and another are equal"""
        return (self.type_ == other.type_ and self.contents == other.contents)
    
    
if __name__ == '__main__':
    
    # Test code
    assert Value(Value.T_EMPTY, 'e').type_less(Value(Value.T_FILE, 'f'))
    assert not Value(Value.T_EMPTY, 'e').type_less(Value(Value.T_EMPTY, 'f'))
    assert Value(Value.T_DIR, 'd').type_greater(Value(Value.T_FILE, 'f'))
    assert Value(Value.T_EMPTY, 'e').equals(Value(Value.T_EMPTY, 'e'))
    assert not Value(Value.T_EMPTY, 'e').equals(Value(Value.T_EMPTY, 'f'))
    print("Tests done")
    
