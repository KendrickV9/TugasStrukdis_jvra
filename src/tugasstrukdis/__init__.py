import javalang
import javalang.tree as jt
from dataclasses import dataclass
from collections import defaultdict
from .graph import Graph


INDENTATION = 4


@dataclass
class Variable:
    type: str
    name: str
    life_start: int
    life_end: int

    def __str__(self):
        return f"{self.type} {self.name}: {self.life_start} - {self.life_end}"


def interfere(var1: Variable, var2: Variable) -> bool:
    """Return true if two variables overlap or false otherwise"""
    return max(var1.life_start, var2.life_start) <= min(var1.life_end, var2.life_end)


def build_interference_matrix(
    var_list: list[Variable],
) -> defaultdict[str, dict[str, bool]]:
    """Creates a intereference matrix for a variable list as a nested dictionary"""
    matrix: defaultdict[str, dict[str, bool]] = defaultdict(dict)
    for var1 in var_list:
        for var2 in var_list:
            matrix[var1.name][var2.name] = interfere(var1, var2)

    return matrix


def parse_method(java_method: jt.MethodDeclaration) -> list[Variable]:
    """Obtain a list of local variables for a method"""
    lvt: dict[str, Variable] = {}

    ending_position: int = java_method.body[-1].position.line
    for statement in java_method.body:
        if isinstance(statement, jt.LocalVariableDeclaration):
            declarators: jt.LocalVariableDeclaration = statement
            for declarator in declarators.declarators:
                var = Variable(
                    declarators.type.name,
                    declarator.name,
                    statement.position.line,
                    ending_position,
                )
                lvt[var.name] = var

    for _, reference in java_method.filter(jt.MemberReference):
        if reference.member in lvt:
            lvt[reference.member].life_end = reference.position.line
    return list(lvt.values())


def parse_class(java_class: jt.ClassDeclaration, depth=0) :
    class_data = {
        "class_name": java_class.name,
        "methods": [],
        "inner_classes": [] # Menampung inner class (rekursif)
    }
    for statement in java_class.body:
        if isinstance(statement, jt.MethodDeclaration):
            print(f"{depth * INDENTATION * ' '}{statement.name}()")
            vl: list[Variable] = parse_method(statement)
            for variable in vl:
                print(f"{(depth + 1) * INDENTATION * ' '}{variable}")
            print(build_interference_matrix(vl))
        elif isinstance(statement, jt.ClassDeclaration):
           inner_class_data = parse_class(statement) # Panggil fungsi ini lagi (rekursif)
           class_data["inner_classes"].append(inner_class_data)
    return class_data

def analyze_java_code(code: str):
  try:

    ast = javalang.parse.parse(code)
    all_classes_data=[]
    for node in ast.types:
        if isinstance(node,jt.ClassDeclaration):
           result=parse_class(node)
           all_classes_data.append(result)
    return {"data": all_classes_data}

  except Exception as e:
        return {"error": str(e)}

       
