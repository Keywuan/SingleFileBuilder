import ast, os

class ParserError(Exception):
    pass

def handle_class(node):

    class_items = []

    for i in node.body:
        if type(i) == ast.FunctionDef:
            func_scope = "%s::%s" % (node.name, i.name)
            class_items.append(func_scope)
        elif type(i) == ast.ClassDef:
            class_scope = "%s::%s" % (node.name, i.name)
            class_items.append(handle_class(i))
    return class_items

def log(msg, indents=0, show_prefix = True, prefix="Builder", new_line=False):
    indent_char = "  "

    if show_prefix == False:
        print("%s-> %s" % ((indent_char * indents), msg))
    else:
        print("%s-> %s: %s" % ((indent_char * indents), prefix, msg))


def parse_file(file_path):
    # Check if path given is valid:
    if not os.path.isdir(file_path):
        raise ParserError("The specified path does not exist.")
    
    # Check if folder is empty
    if len(os.listdir(file_path)) == 0:
        raise ParserError("The specified folder is empty.")
    
    # Used to store data about each file in the project.
    project_files = []

    # Loop through the project folder, only grabbing files with python extensions.
    for f in [x for x in os.listdir(file_path) if x.endswith(".py") or x.endswith(".pyw")]:
        with open("%s\\%s" % (file_path, f), "r") as project_file:
            file_data = {
                "file-name":f,
                "file-body":project_file.read()
            }
            project_files.append(file_data) # Store all data about the file in a list.

    log("Loaded %s files from project for compilation." % (len(project_files)))

    log("Parsing project files into usable format.")
    for f in project_files:
        log("Parsing file '%s':" % (f["file-name"]), indents=1, show_prefix=False)

        parsed_file = ast.parse(f["file-body"], "-", "exec")

        for node in parsed_file.body[:]: # Function Def
            if type(node) == ast.Assign:
                print(node.value)

parse_file("C:\\Users\\Kiwan\\Documents\\PythonScript\\Script\\")
input()