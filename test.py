
from command import Command
from node import Node
from value import Value

c = Command(Node(['d1', 'd2', 'f1']), Value(Value.T_EMPTY, 'e'), Value(Value.T_DIR, 'd'))
print(c.as_string())
print(c.is_constructor())
