# unittestmaker
Simplify unittest creation with recording

## Setup
You can retrive from github with:
```
$ git clone https://github.com/kavod/unittestmaker.git
```
Then, in the current directory (parent of the project folder), just type:
```
$ sudo pip install unittestmaker/
```
or, if you wish to install without root permissions:
```
$ pip install --user unittestmaker/
```
## Usage
```
$ python -m testMaker
```

## Example
Let's create a simple class:
**Robot.py**
```python
#!/usr/bin/env python
from __future__ import print_function

class Robot(object):
	def __init__(self,name="Johnny V"):
		self.myName = name
		self.urName = None
		
	def meet(self):
		print("Hi! My name is {0}. WHat's yours?".format(self.myName))
		self.urName = raw_input("> ")
		print("Nice to meet you {0}".format(self.urName))
		
	def whoami(self):
		if self.urName is None:
			raise Exception("I don't know you!")
		else:
			print("You are my friend {0}".format(self.urName))
```
The aim is to create quickly a `unittest` script for this class.

Let's call `testmaker`:
```{r, engine='bash', count_lines}
$ python -m testMaker
Run commands: (type Ctrl+D to finish)
>>>
```
Now, by the same way if I had done with classic python interpretor, I will test my class:
```{r, engine='bash', count_lines}
Run commands: (type Ctrl+D to finish)
>>> import Robot
>>> johnny=Robot.Robot()
>>> johnny.whoami()
    ^
Exception:I don't know you!
>>> johnny.meet()
Hi! My name is Johnny V. WHat's yours?
> Boris
Nice to meet you Boris
>>> johnny.whoami()
You are my friend Boris
>>>
```
After pushing Ctrl+D to exit, testMaker will create the script and run it to be sure recording is OK:
```{r, engine='bash', count_lines}
>>> ^D
Building test script...
Running test script...
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
OK, please indicate a name for your test:
>
```
Let's name our script now.
```{r, engine='bash', count_lines}
OK, please indicate a name for your test:
>robot1
Test script saved in test_robot1
Just type `python -m unittest tests.test_robot1` in order execute it.
Otherwise `python -m unittest discover` in order execute all tests in subdirectories.
$ 
```
The file tests/test_robot1.py has been created automatically. You can now type `python -m unittest tests.test_robot1` in order to re-run the test script when required.
```{r, engine='bash', count_lines}
$ `python -m unittest tests.test_robot1`
.
----------------------------------------------------------------------
Ran 1 test in 0.002s

OK
```

### Generated unittest watch the print output!
Now, imagine you made few evolutions on your class. For example, we switch "Hi!" formula to "Good morning":
**Robot.py**
```python
#!/usr/bin/env python
from __future__ import print_function

class Robot(object):
	def __init__(self,name="Johnny V"):
		self.myName = name
		self.urName = None
		
	def meet(self):
		print("Good morning! My name is {0}. WHat's yours?".format(self.myName))
		self.urName = raw_input("> ")
		print("Nice to meet you {0}".format(self.urName))
		
	def whoami(self):
		if self.urName is None:
			raise Exception("I don't know you!")
		else:
			print("You are my friend {0}".format(self.urName))
```
The aim is to create quickly a `unittest` script for this class.

Let's call `testmaker`:

Running the unittest will detect regressions since the stdoutput has changed:
```{r, engine='bash', count_lines}
$ python -m unittest tests.test_robot1
F
======================================================================
FAIL: test_robot1 (tests.test_robot1.Test_robot1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 1305, in patched
    return func(*args, **keywargs)
  File "tests/test_robot1.py", line 29, in test_robot1
    call('Nice to meet you Boris')])
AssertionError: [call("Good morning! My name is Johnny V. WHat's yours?"),
 call('Nice to meet you Boris')] != [call(u"Hi! My name is Johnny V. WHat's yours?"), call(u'Nice to meet you Boris')]

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```

### Generated unittest also watch the number of user inputs!
In the same way, if meet method required a new additionnal user input, the unittest will failed since it has been recorded with only 1 input ("Boris" in our example)
**Robot.py**
```python
#!/usr/bin/env python
from __future__ import print_function

class Robot(object):
        def __init__(self,name="Johnny V"):
                self.myName = name
                self.urName = None

        def meet(self):
                print("Hi! My name is {0}. WHat's yours?".format(self.myName))
                self.urName = raw_input("> ")
                print("Nice to meet you {0}".format(self.urName))
                print("How old are you?")
                self.urAge = raw_input("> ")

        def whoami(self):
                if self.urName is None:
                        raise Exception("I don't know you!")
                else:
                        print("You are my friend {0}".format(self.urName))
```

```{r, engine='bash', count_lines}
$ python -m unittest tests.test_robot1
E
======================================================================
ERROR: test_robot1 (tests.test_robot1.Test_robot1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 1305, in patched
    return func(*args, **keywargs)
  File "tests/test_robot1.py", line 27, in test_robot1
    johnny.meet()
  File "Robot.py", line 14, in meet
    self.urAge = raw_input("> ")
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 1062, in __call__
    return _mock_self._mock_call(*args, **kwargs)
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 1121, in _mock_call
    result = next(effect)
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 127, in next
    return _next(obj)
StopIteration

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (errors=1)
```

### Generated unittest also watch the Exception raised

testMaker has recorded the raised exceptions and resulting unittest will ensure the same exceptions will be raised in the same way.
**Robot.py**
```python
#!/usr/bin/env python
from __future__ import print_function

class Robot(object):
        def __init__(self,name="Johnny V"):
                self.myName = name
                self.urName = "Joe Doe" # <== replaced from None
                
        def meet(self):
                print("Hi! My name is {0}. WHat's yours?".format(self.myName))
                self.urName = raw_input("> ")
                print("Nice to meet you {0}".format(self.urName))
                
        def whoami(self):
                if self.urName is None:
                        raise Exception("I don't know you!")
                else:
                        print("You are my friend {0}".format(self.urName))
```
```{r, engine='bash', count_lines}
$ python -m unittest tests.test_robot1
F
======================================================================
FAIL: test_robot1 (tests.test_robot1.Test_robot1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/usr/local/lib/python2.7/dist-packages/mock/mock.py", line 1305, in patched
    return func(*args, **keywargs)
  File "tests/test_robot1.py", line 23, in test_robot1
    johnny.whoami()
AssertionError: Exception not raised

----------------------------------------------------------------------
Ran 1 test in 0.003s

FAILED (failures=1)
```
### Extra feature: assert function will be turned to unittest's assertTrue method
If you record an "assert" command in your recording, it will automatically be replaced by self.assertTrue method of unittest class.


