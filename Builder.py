import ast, os, copy

class ConversionError(Exception):
    pass

class ProjectConverter:


    def __init__(self, project_folder, main_file_name="main.py"):
        self.project_folder = project_folder
        self.entry_file = main_file_name

        if not os.path.exists(self.project_folder):
            raise ParserError("Specified folder does not exist.")
        
        elif len(os.listdir(self.project_folder)) == 0:
            raise ParserError("Specified folder is empty.")

        elif len([x for x in os.listdir(self.project_folder) if x.endswith(".py") or x.endswith(".pyw")]) == 0:
            raise ParserError("Specified folder is not a python project folder.")

        self.project_files = [x for x in os.listdir(self.project_folder) if x.endswith(".py") or x.endswith(".pyw")]

        self.parsed_declares = {
            "functions":{

            },
            "variables":{

            },
            "classes":{

            }
        }

        self.parsed_imports = []

        self.static_classes = {

        }

    def parse_project(self):
        for f in self.project_files:
            file_path = "%s\\%s" % (self.project_folder, f)
            
            print("-> Parser: Parsing file '%s'" % (f))

            with open(file_path, "r") as fopen:
                file_lines = fopen.readlines()
                file_tree = ast.parse("".join(file_lines), "-", "exec")

                self.handle_module(file_tree)
                
                self.static_classes.update({
                    f.replace(".py", ""):{
                        "Imports":copy.deepcopy(self.parsed_imports),
                        "Body":"",
                        "Declares":copy.deepcopy(self.parsed_declares)
                    }
                })

                self.parsed_declares = {  "functions":{  }, "variables":{ }, "classes":{ }}
                self.parsed_imports.clear()

                print("-> Parser: Parsed %s imports" % (len(self.static_classes[f.replace(".py", "")]["Imports"])))
                print("-> Parser: Parsed %s classes" % (len(self.static_classes[f.replace(".py", "")]["Declares"]["classes"])))
                print("-> Parser: Parsed %s Functions" % (len(self.static_classes[f.replace(".py", "")]["Declares"]["functions"])))
                print("-> Parser: Parsed %s Variables\n" % (len(self.static_classes[f.replace(".py", "")]["Declares"]["variables"])))

                for idx, line in enumerate(file_lines):
                    if not line.startswith("import") and not line.startswith("from"):
                        self.static_classes[f.replace(".py", "")]["Body"] = copy.deepcopy("".join(file_lines[idx:]))
                        break

                #print(self.static_classes[f.replace(".py", "")]["Body"])
    
    def build_project(self):
        print("-> Builder: Building output file 'Output.py' from parsed project.")

        import_order = []
        custom_import_order = []
        for key in self.static_classes.keys():
           
            print("   -> Processing imports for file.")
           
            for i in [f for f in self.static_classes[key]["Imports"] if type(f) != list and f.startswith("import")]:
                import_name = i.split(" ")[1]

                if import_name in [x.replace(".py", "") for x in os.listdir(self.project_folder)]:
                    print("      -> Custom import not used: '%s.py'" % (import_name))
                    custom_import_order.append(i.replace("import ", ""))
                else:
                    print("      -> Standard import used: '%s.py'" % (import_name))
                    import_order.append(i)
            
            for i in [f for f in self.static_classes[key]["Imports"] if type(f) == list]:
                module = i[0]
                imported = i[1]

                if module in [x.replace(".py", "") for x in os.listdir(self.project_folder)]:
                    print("      -> Custom import from not used: from '%s.py' import '%s'" % (module, imported))
                    custom_import_order.append(module)
                else:
                    print("      -> Import from used: from '%s.py' import '%s'" % (module, imported))

                import_order.append("from %s import %s" % (module, imported))

        output_file = "#   IMPORTS\n"
        output_file += "\n".join(import_order)
        
        for i in custom_import_order:
            output_file += "\n\n#   DEPENDENCY '%s.py'" % (i)
            class_definition = "class %s(object):" % (i)
            
            output_file += "\n%s\n" % (class_definition)
            for line in self.static_classes[i]["Body"].split("\n"):
                output_file += "    %s\n" % (line)
                    
        print(output_file)
               
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
            elif type(elem) == ast.Assign:
                self.handle_vardef(elem, scope_name)
            elif type(elem) == ast.Import:
                self.handle_import(elem)
            elif type(elem) == ast.ImportFrom:
                self.handle_import_from(elem)

    def handle_import(self, node):
        names = [name.name for name in node.names]
        
        for name in names:
            print("    -> Import '%s' usage discovered" % (name))
            self.parsed_imports.append("import %s" % (name))

        return

    def handle_import_from(self, node):

        module_name = node.module
        imported = [node.name for node in node.names]

        print("    -> From '%s' import '%s' usage discovered" % (module_name, ",".join(imported)))

        self.parsed_imports.append([module_name, ",".join(imported)])

        return

    def handle_classdef(self, node, parent_name):
        scope_class = "%s::%s" % (parent_name, node.name)
        if scope_class.startswith("::"):
            scope_class = "".join(list(scope_class)[2:])

        if parent_name == "":
            print("    -> Class '%s' discovered" % (scope_class))
        else:
            print("        -> Subclass '%s' discovered" % (scope_class))

        
        self.parsed_declares["classes"].update({
            "%s" % (node.name):{
                "scope":"::".join(scope_class.split("::")[:-1])
            }
        })


        self.walk(node, "%s::%s" % (parent_name, node.name))
        return

    def handle_funcdef(self, node, parent_name):
        scope_func = "%s::%s" % (parent_name, node.name)
        if scope_func.startswith("::"):
            scope_func = "".join(list(scope_func)[2:])

        print("    -> Function '%s' discovered" % (scope_func))

        func_args = []
        try:
            func_args = ([arg.arg for arg in node.args.args])
        except:
            pass # No arguments

        # Store processed function.
        self.parsed_declares["functions"].update({
            "%s" % (node.name):{
                "args":func_args,
                "scope":"::".join(scope_func.split("::")[:-1])
            }
        })

        self.walk(node, "%s::%s" % (parent_name, node.name))
        return

    def handle_vardef(self, node, parent_name):
        scope_var = "%s::%s" % (parent_name, node.targets[0].id)
        if scope_var.startswith("::"):
            scope_var = "::".join(scope_var.split("::")[:-1])
        

        if not node.targets[0].id in self.parsed_declares["variables"]:
            print("    -> Variable '%s' discovered" % (scope_var))

            self.parsed_declares["variables"].update({
                "%s" % (node.targets[0].id):{
                    "scope":scope_var.split("::")[:-1]
                }
            })


        return

    def handle_module(self, node):
        self.walk(node, "")
    
    def output_final_file(self, obfuscate=False, minify=False, randomize=False, junkcode=False):
        pass


cvt = ProjectConverter("C:\\Users\\Kiwan\\Documents\\PythonScript\\Script")

cvt.parse_project()
cvt.build_project()