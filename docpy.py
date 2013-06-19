#! /usr/bin/python
"""
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
with one exception: '_' (underscore).
Since underscores are widely used in function and variable names,
all underscores are escaped prior to parsing, except when between backticks.
You can use the '*' (asterisk) tag for the same result.

Last note:
This documentation was generated using... *self!* 
"""

import tokenize
from token import STRING, NAME, OP, INDENT, DEDENT
import re
import sys

merge_newlines_regex = re.compile(r'[\n|\r\n|\n\r]{2,}')
leading_space_regex = re.compile(r'\s*')
unquote_code_regex = re.compile(r"`[^`]*\`")

IGNORE_UNDOCUMENTED = True

current_module = ''
current_class = ''
has_classes_title = False
all_list = []

__all__ = ['DocModule']

class BlockExit(Exception):
    pass
    
class Stack:
    def __init__(self, _stack=None):
        self.items = _stack or []
        
    def push(self, item):
        if item:
            self.items.append(item)
        return self
            
    def pop(self, i):
        self.items.pop(i)
        return self
        
    def __len__(self):
        return len(self.items)
        
    def __getitem__(self, i):
        return self.items[i]
        
    def __iter__(self):
        return iter(self.items)
        
class G:
    g = None
    last_item = None
    _rollback = False
    
    def __init__(self, g=None):
        if g:
            self.__class__.g = g
        
    def __iter__(self):
        if self.__class__._rollback:
            self.__class__._rollback = False
            yield self.__class__.last_item
            
        for item in self.__class__.g:
            item = item[:2]
            self.__class__.last_item = item
            yield item
        
    def next(self):
        if self.__class__._rollback:
            self.__class__._rollback = False
            return self.__class__.last_item
            
        item = self.__class__.g.next()[:2]
        self.__class__.last_item = item
        return item
        
    def rollback(self):
        self.__class__._rollback = True
        
        
def find_docstring():
    indents = 0
    while True:
        tok_type, token = G().next()
        if tok_type == NAME:
            if token in ('class', 'def'):
                G().rollback()
            elif token == '__all__':
                get_all_list()
            return ''
        elif tok_type == INDENT:
            indents += 1
        elif tok_type == STRING and (token.startswith("'''") or token.startswith('"""')):
            doc_ = token.strip("'''").strip('"""').strip('\n').replace('_', '\_')
            n = len(leading_space_regex.match(doc_).group())
            doc_ = '\n'.join([line[n:] for line in doc_.splitlines()])
            doc_ = unquote_code_regex.sub(lambda x:x.group(0).replace('\_','_'), doc_)
            return doc_
    
def find_class_or_function(types=('class', 'def'), **kwargs):
    indents = 0
    while True:
        tok_type, token = G().next()
        if tok_type == NAME and token in types:
            if token == 'class':
                klass = doc_class(**kwargs)
                return klass
            else:
                func = doc_function(**kwargs)
                return func
        elif tok_type == NAME and token == '__all__':
            get_all_list()
        elif tok_type == INDENT:
            indents += 1
        elif tok_type == DEDENT:
            indents -= 1
            if indents < 0:
                raise BlockExit
    
def find_method():
    return find_class_or_function(('def',), is_method=True)
    
def find_colons():
    stack = Stack()
    while True:
        tok_type, token = G().next()
        stack.push(token)
        if tok_type == OP and token == ':':
            if stack:
                return stack[1:-2]
            return stack

def exit_block():
    indents = 0
    while True:
        tok_type, token = G().next()
        if tok_type == INDENT:
            indents += 1
        elif tok_type == DEDENT:
            indents -= 1
            if indents < 0:
                break
        
def get_all_list():
    global all_list
    tok_type, token = G().next() # '=' sign
    tok_type, token = G().next() # '[' or '(' sign
    closing_op = ']' if token == '[' else ')'
    stack = Stack()
    while True:
        tok_type, token = G().next()
        if token == closing_op:
            all_list = list(stack.items)
            return
        elif tok_type == STRING:
            stack.push(token.strip("'").strip('"'))
        
    
def doc_function(is_method=False):
    stack = Stack()
    name = G().next()[1]
    if name.startswith('_') and name != '__init__':
        result = []
        return
        
    name = name.replace('_', '\_')
    class_name = current_class + '.' if current_class else ''
    func_name = '##### %s.%s**%s**' % (current_module, class_name, name)
    args = find_colons()
    if args:
        if args[0] == 'self':
            args.pop(0)
            if args:
                args.pop(0)
    arg_string = ''.join(args)
    arg_string = ', '.join(arg_string.split(',')).replace('_', '\_').replace('*', '\*')
    if arg_string:
        arg_string = '_%s_' % arg_string
    stack.push('%s(%s)' % (func_name, arg_string))
    
    doc_ = find_docstring()
    stack.push(doc_)
    
    exit_block()
    
    if (not is_method and all_list and name.replace('\_', '_') not in all_list) \
        or (IGNORE_UNDOCUMENTED and not doc_):
        result = []
    else:
        result = stack
        
    return '\n'.join(result)

        
def doc_class():
    global current_class, has_classes_title
    
    stack = Stack()
    if not has_classes_title:
        stack.push('### Classes')
    
    name = G().next()[1].replace('_', '\_')
    stack.push('#### _class_ %s.**%s**' % (current_module, name))
    current_class = name
    
    # Loop until ':'
    find_colons()
    
    doc_ = find_docstring()
    stack.push(doc_)
    
    # Loop methods
    while True:
        try:
            method = find_method()
            stack.push(method)
        except BlockExit:
            break
    
    # Finishes
    current_class = ''
    if (all_list and name.replace('\_', '_') not in all_list) \
        or (IGNORE_UNDOCUMENTED and not doc_):
        result = []
    else:
        has_classes_title = True
        result = stack
        
    return '\n'.join(result)
        
class DocModule:
    """
    The class that starts the documentation process.
    Usage:
    
        d = DocModule('mymodule.py')
        print d
    """
    def __init__(self, filename):
        """Pass `filename` to document"""
        global current_module, has_classes_title, all_list
        try:
            f = open(filename)
        except IOError:
            return
        module_name = filename.rsplit('/', 1)[-1].replace('_', '\_')
        
        current_module = module_name.replace('.py', '')
        has_classes_title = False
        all_list = []
        
        g = tokenize.generate_tokens(f.readline)
        G(g)
        stack = Stack()
        stack.push('## %s' % module_name)
        
        doc_ = find_docstring()
        stack.push(doc_)
        
        # Loop classes
        while True:
            try:
                callable_ = find_class_or_function()
                stack.push(callable_)
            except (BlockExit, StopIteration):
                break
        
        self.result = stack

    def __repr__(self):
        return '\n'.join(self.result)
        
        
if __name__ == '__main__':
    try:
        module = sys.argv[1]
    except IndexError:
        print "Please provide a module name"
        exit(1)

    d = DocModule(module)
    print d
    
