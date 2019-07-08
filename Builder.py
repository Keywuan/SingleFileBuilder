import ast, os

class ParserError(Exception):
    pass

class ProjectParser:


    def __init__(self, project_folder, main_file_name="main.py"):
        self.project_folder = project_folder

        if not os.path.exists(self.project_folder):
            raise ParserError("Specified folder does not exist.")
        
        elif len(os.listdir(self.project_folder)) == 0:
            raise ParserError("Specified folder is empty.")

        elif len([x for x in os.listdir(self.project_folder) if x.endswith(".py") or x.endswith(".pyw")]) == 0:
            raise ParserError("Specified folder is not a python project folder.")

        self.project_files = [x for x in os.listdir(self.project_folder) if x.endswith(".py") or x.endswith(".pyw")]

    def parse_project(self):
        for f in self.project_files:
            file_path = "%s\\%s" % (self.project_folder, f)
            
            with open(file_path, "r") as fopen:
                file_tree = ast.parse(fopen.read(), "-", "exec")
                self.handle_module(file_tree)

    def get_file_count(self):
        return len(self.project_files)

    def walk(self, node, scope_name):
        elements = node.body

        for elem in elements:
            
            # Classify element/node.
            if type(elem) == ast.ClassDef:
                self.handle_classdef(elem, scope_name)
            elif type(elem) == ast.FunctionDef:
                self.handle_funcdef(elem, scope_name)


    def handle_classdef(self, node, parent_name):
        if parent_name != "":
            parent_name = "::%s" % (parent_name)

        print("-> Class '%s::%s' discovered" % (parent_name, node.name))
        self.walk(node, "%s::%s" % (parent_name, node.name))
        pass

    def handle_funcdef(self, node, parent_name):
        if parent_name != "":
            parent_name = "::%s" % (parent_name)

        print("-> Function '%s::%s' discovered" % (parent_name, node.name))
        self.walk(node, "%s::%s" % (parent_name, node.name))
        pass

    def handle_module(self, node):
        self.walk(node, "")
    
    def output_final_file(self, obfuscate=False, minify=False, randomize=False, junkcode=False):
        pass


parser = ProjectParser("C:\\Users\\Kiwan\\Documents\\PythonScript\\Script")

parser.parse_project()