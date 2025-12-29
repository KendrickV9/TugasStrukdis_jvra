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


def parse_class(java_class: jt.ClassDeclaration, depth=0) -> None:
    """Parse a Java class, parsing it's methods and inner classes"""
    print(f"{depth * INDENTATION * ' '}{java_class.name}$")
    depth += 1
    for statement in java_class.body:
        if isinstance(statement, jt.MethodDeclaration):
            print(f"{depth * INDENTATION * ' '}{statement.name}()")
            vl: list[Variable] = parse_method(statement)
            for variable in vl:
                print(f"{(depth + 1) * INDENTATION * ' '}{variable}")

            # print(build_interference_matrix(vl))
            graph = Graph(build_interference_matrix(vl))

        elif isinstance(statement, jt.ClassDeclaration):
            parse_class(statement, depth=depth)


def main() -> None:
    """Main function"""
    code: str
    with open("assets/Sample.java") as f:
        code = f.read()

    ast = javalang.parse.parse(code)

    first: bool = True
    for node in ast.types:
        if first:
            first = False
        else:
            print("")

        if isinstance(node, jt.ClassDeclaration):
            parse_class(node)
