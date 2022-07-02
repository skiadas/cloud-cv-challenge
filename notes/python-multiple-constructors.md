# Python multiple constructors

Following along with [this tutorial](https://realpython.com/python-multiple-constructors/) on how to have multiple constructors in Python. It appears there are fundamentally three ways:

- Use optional arguments and type checking to simulate multiple constructors
- Write multiple constructors using the built-in `@classmethod` decorator
- Overload your class constructors using the `@singledispatchmethod` decorator

The standard way to initialize an object in Python is the `__init__` method. It is automatically called when we use the normal `className(params)` way of creating new objects.

However there is another special method, called `__new__`, that happens first. This method takes the class as input and returns a new object of that class (or some times of another class). If it returns an instance of the class itself, then `__init__` will get called. There is a default implementation of this method that we normally don't need to mess with.

We can't use the normal method overloading that languages like Java offer, because Python internally stores methods in a `__dict__` property which is a dictionary.

Another cool special method, though not related to the task at hand, is `__call__` which makes it possible for us to *call* the objects we created, i.e. to use them as functions.

## Multiple constructors via optional arguments

One way to approach having multiple constructors is to use optional arguments to `__init__` with default values, or to check the type of the arguments and act accordingly. Here is such an example:
```python
def __init__(self, exponent=2, *, start=0):
```
The asterisk there indicates that all arguments following it can only be specified by name, and no longer by position.

Thinking for my use case, I don't think this would work for me. I need to do a lot of legwork that is different in the two cases: I need to call a table-creation method in the one case, and I need to query an existing table in order to set values in the other case.

Actually thinking about it some more, this *can* be useful. I see three different usage patterns for my class:

- Create a new table
- Provide access to an existing table where the key information is given to you
- Provide access to an existing table where the key information is to be read from the table. I don't think I will need this third case, but distinguishing between the 2nd and 3rd case could be done via optional arguments.

## Using @classmethod to provide multiple constructors

Class methods receive the class itself as a first parameter, rather than an object. They can then rely on calling the constructor themselves. This seems viable for my use case, so I will attempt to move the table-creation method there.

This worked rather smoothly. I now have a `dbtable.create` method for when I need to actually create the table (namely in my tests). I will keep reading to see the other approaches though.

## Using @singledispatchmethod

This decorator allows us to turn a method into a "generic single dispatch method", meaning that it will dispatch to different other methods based on the type of its argument. It is available in the `functools` package.

This requires some awkward tooling. first you need a method annotated with @singledispatchmethod. Then you need to use that method as a decorator like `@generic_method.register(str)` to implement the method that works when the first argument is of type string.

So the first fundamental limitation, beyond the awkward syntax, is that this only dispatches on type, which isn't exactly what I was looking for. It also only dispatches on one parameter. Definitely not a fan of this technique.

