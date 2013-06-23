## docpy.py
A lightweight simple automatic documentor for Python modules.  
  
**No special syntax or characters are required.**  
All you have to do is make sure your code is documented according to PEP-8   
recommendations.  
  
**No imports are performed**  
Your files will be opened for read like regular text file, so dependencies are   
not an issue.  
  
**docpy** will go through the classes, methods and functions of the module,  
parse their argument structure and docstrings, and construct a Markdown output.  
Finally, the Markdown will be converted to HTML to produce a styled document.  
  
Usage:  
  
    $ ./docpy.py [-m] [-a] filename/package  
  
Output:    
    An HTML documentation of your code.  
    If you provide a file as input, the output will be directed to the console.  
    If you provide a package name, all modules and packages within this package   
    will be documented, and an HTML file will be created for each package under the   
    a folder named '*package*\_docs'.  
      
Optional arguments:  
    `-m` - will force a Markdown output. By default, output is converted to HTML.  
    `-a` - will force documenting undocumented objects (see notes below).  
      
Notes:  
  
* **Private methods/functions**: Methods or functions starting with an underscore  
(eg `_my_function()`) will be ignored, except for `__init__`.  
* **Undocumented objects**: Functions/methods/classes without a **docstring**   
will be ignored (nothing to document, right?).  
You can change this behaviour by spceifying `-m` in the command line.  
* **Scope**: **docpy** will document *every* object (except for those ignored   
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

##### docpy.DocModule.**\_\_init\_\_**(_filename, add\_ref=False_)
Pass `filename` to document
