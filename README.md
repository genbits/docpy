## docpy.py
A lightweight simple automatic documentor for Python modules.
The module is not imported. Instead, it is opened for read like regular text file, 
so dependencies are not an issue.
This script will go through the classes, methods and functions
of the module, parse their argument structure and docstrings,
and construct a MarkDown output for documentation purposes.

All you have to do is make sure your code is documented according to PEP-8 
recommendations.

Usage:

    $ ./docpy.py filename

Output:
    A MarkDown of *filename*
    
Notes:

* **Private methods/functions**: Methods or functions starting with an underscore
(eg `_my_function()`) will be ignored, except for `__init__`.
* **Undocumented objects**: Functions/methods/classes without a **docstring** 
will be ignored (nothing to document, right?).
You can change this behaviour by setting the `IGNORE_UNDOCUMENTED` flag to **False**.
* **Scope**: **docpy.py** will document *every* object (except for those ignored 
as mentioned above) as long as `__all__` is not defined. If `__all__` is defined, 
only objects on that list will be documented.

MarkDown considerations:
The output is in MD syntax, so you can use any MD tags in your docstrings, 
with one exception: '\_' (underscore).
Since underscores are widely used in function and variable names,
all underscores are escaped prior to parsing, except when between backticks.
You can use the '*' (asterisk) tag for the same result.

Last note:
This documentation was generated using... *self!* 
### Classes
#### _class_ docpy.**DocModule**
The class that starts the documentation process.
Usage:

    d = DocModule('mymodule.py')
    print d

##### docpy.DocModule.**\_\_init\_\_**(_filename_)
Pass `filename` to document
