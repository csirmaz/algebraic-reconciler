# How to Syncronize Many Filesystems in Near Linear Time

## Introduction

This repository hosts sample implementations of the algebraic file synchronization
algorithms described in
Elod P Csirmaz and Laszlo Csirmaz,
How to Syncronize Many Filesystems in Near Linear Time.

## Usage

The inputs of the algorithms are command sequences (instances of CSequence) or command sets (instances of CSet).
Command sequences must be members of a single Session object, which manages the representation of filesystem nodes
and ensures their uniqueness. Command sets can be derived from command sequences.

A session can be initialised using a string representation of command sequences, mimicking
a server receiving and processing filesystem updates from many replicas.

The string representation is as follows. For examples, see below.

- Commands are provided in a `<{path}|{input value}|{output value}>` format
- A path is a list of strings separated by `/`
- A value is a (possibly empty) string prefixed by `E`, `F`, or `D` for the empty, file or directory types
- In sequences, commands are separated by `.`
- A sequence definition is a name for the sequence, followed by `=`, followed by a sequence of commands
- Sequence definitions are separated by `;`
- Sequence objects will be stored under properties of the session object reflecting their names

## Algorithms

### Algorithm 1 (Adding up pointers)

```python
from session import Session
s = Session("a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>")
s.a.add_up_pointers() # defined in csequence.py
```

### Algorithm 2 (Determining if a command set is canonical)

```python
from session import Session
from csequence import CSequence
s = Session("a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>")
print(CSequence.is_set_canonical(s.a.as_set()))
```

### Algorithm 3 (Ordering a canonical set)

```python
from session import Session
from csequence import CSequence
s = Session("a=<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1|E|D>")
print(CSequence.order_set(s.a.as_set()).as_string())
```

### Algorithm 4 (Command sequence to canonical set)

```python
from session import Session
s = Session("a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>.<d1/d2/f3|Ff1|Ff2>")
print(s.a.get_canonical_set().as_string()) # defined in csequence.py
```

### Algorithm 5 (Generating a merger - greedy)

```python
from session import Session
from csequence import CSequence
s = Session("""a=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff1>;
               b=<d1|E|D>.<d1/d2|E|D>.<d1/d2/f3|E|Ff2>""")
merger = CSequence.get_greedy_merger([s.a, s.b]).as_set()
print(merger.as_string())
```

### Algorithm 6 (Checking if canonical sets are refluent)

```python
from session import Session
from csequence import CSequence
s = Session("""a=<1/2|D|E>.<1|D|E>;
               b=<1/2/3|E|D>;
               c=<1/2|D|Ff2>.<0|E|D>;
               d=<1/2/3|E|D>.<1/2/3/4|E|Ff3>;
               e=<1/2/3|E|D>.<1/2/3/4b|E|Ff4>""")
print(CSequence.check_refluent([s.a, s.b, s.c, s.d, s.e]))
```

