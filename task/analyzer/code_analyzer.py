# write your code here
import constants
import sys
import os
import re
import ast


def get_file(filepath):
    try:
        file = open(filepath)
    except IOError as err1:
        print(err1)
    else:
        return file


def check_style_issue(file, path):
    #is_comment = False
    blank_lines = 0
    errors = list()

    for i, line in enumerate(file, start=1):
        if line.isspace():
            #print(f"Line {i} is blank")
            blank_lines = blank_lines + 1
        else:
            #check line length
            line_length = check_line_length(line)
            if line_length:
                errors.append((line_length, i))

            #check indentation
            indent = check_indentation(line)
            if indent:
                errors.append((indent, i))

            if '#' in line:
                code, comment = line.split('#', 1)
            else:
                code, comment = line, ""
            if code.strip().endswith(';'):
                errors.append((constants.S003, i))
            inline = check_inline(line)
            if inline:
                errors.append((inline, i))
            if 'todo' in comment.lower():
                errors.append((constants.S005, i))
            if blank_lines > 2:
                errors.append((constants.S006, i))
            blank_lines = 0
            if code.strip().lower().startswith('def'):
                funct_errors = check_func(line)
                for err in funct_errors:
                    errors.append((err, i))
            if code.strip().lower().startswith('class'):
                class_errors = check_class(line)
                for err in class_errors:
                    errors.append((err, i))
        #errors += check_ast(line)

    errors += check_ast(open(path))
    errors = sorted(errors, key=lambda x: x[1])
    [print(f'{path}: Line {error[1]}: {error[0]}') for error in errors]


def check_inline(line):
    #print(line)
    comment_index = line.lstrip().find('#')
    #print(comment_index)
    if comment_index > 0:
        if not(line[comment_index-1].isspace() and line[comment_index-2].isspace()):
            return constants.S004
    return ''


def check_indentation(line):
    if not line.isspace() and ((len(line) - len(line.lstrip())) % 4):
        return constants.S002
    return ''


def check_line_length(line):
    if len(line) > constants.PEP_LINE_MAX:
        return constants.S001
    return ''


def check_class(line):
    errors = []
    class_name = line.split('class')[1]
    if len(class_name) - len(class_name.lstrip()) > 1:
        errors.append(constants.S007.replace('constructor', 'class'))
    class_name = re.split('[:(]', class_name, 1)[0].lstrip()
    if re.match('[A-Z][A-Za-z0-9]*', class_name) is None:
        errors.append(constants.S008.replace('insert_name', class_name))
    return errors


def check_func(line):
    errors = []
    funct_name = line.split('def')[1]
    if len(funct_name) - len(funct_name.lstrip()) > 1:
        errors.append(constants.S007.replace('constructor', 'def'))
    funct_name = funct_name.split('(')[0].lstrip()
    if re.match('[a-z0-9_]+', funct_name) is None:
        errors.append(constants.S009.replace('constructor', funct_name))
    return errors


def check_ast(line):
    tree = ast.parse(line.read())
    error = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            #check args for snake case
            for a in node.args.args:
                if not check_snake_case(a.arg):
                    error.append((constants.S010.replace('insert_name', a.arg), node.lineno))

            #check default values for mutable type
            for a in node.args.defaults:
                if isinstance(a, ast.List):
                    error.append((constants.S012, node.lineno))

        #check for snake case in variable names
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store):
                if not check_snake_case(node.id):
                    error.append((constants.S011, node.lineno))
    return error


def check_snake_case(name):
    return bool(re.match('[a-z0-9_]+', name))


def main():
    path = sys.argv[1]
    if os.path.isdir(path):
        for entry in os.listdir(path):
            if entry.endswith('.py'):
                new_path = os.path.join(path, entry)
                file = get_file(new_path)
                check_style_issue(file, new_path)
    else:
        if path.endswith('.py'):
            file = get_file(path)
            check_style_issue(file, path)


if __name__ == '__main__':
    main()
