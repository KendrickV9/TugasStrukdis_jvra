import javalang
import javalang.tree as jt
from dataclasses import dataclass


@dataclass
class Variable:
    type: str
    name: str

    def __str__(self):
        return f"{self.type} {self.name}"


def get_local_variables(java_method: jt.MethodDeclaration) -> list[Variable]:
    local_variables: list[Variable] = []
    for statement in java_method.body:
        if isinstance(statement, jt.LocalVariableDeclaration):
            declarators: jt.LocalVariableDeclaration = statement
            for declarator in declarators.declarators:
                local_variables.append(Variable(declarators.type.name, declarator.name))

    return local_variables


def parse_class(java_class: jt.ClassDeclaration, depth=0) -> None:
    print(f"{depth * 2 * ' '}{java_class.name}$")
    depth += 1
    for method in java_class.methods:
        print(f"{depth * 2 * ' '}{method.name}()")
        for variable in get_local_variables(method):
            print(f"{(depth + 1) * 2 * ' '}{variable}")


def main() -> None:
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
