from __future__ import annotations
import javalang
import javalang.tree as jt
from dataclasses import dataclass
from collections import defaultdict


INDENTATION = 4


@dataclass
class Variable:
    type: str
    name: str
    life_start: int
    life_end: int

    @staticmethod
    def interfere(var1: Variable, var2: Variable) -> bool:
        """Return true if two variables overlap or false otherwise"""
        return max(var1.life_start, var2.life_start) <= min(
            var1.life_end, var2.life_end
        )

    def __str__(self):
        return f"{self.type} {self.name}: {self.life_start} - {self.life_end}"


class JavaMethod:
    def __init__(self, javalang_method: jt.MethodDeclaration) -> None:
        self.name: str = javalang_method.name
        self.variables: list[Variable] = []
        self.interference_matrix: defaultdict[str, dict[str, bool]]
        self.start_line: int = javalang_method.body[0].position.line - 1
        self.end_line: int = javalang_method.body[-1].position.line + 1
        print(self.start_line, self.end_line)

        lvt: dict[str, Variable] = {}

        for statement in javalang_method.body:
            if isinstance(statement, jt.LocalVariableDeclaration):
                declarators: jt.LocalVariableDeclaration = statement
                for declarator in declarators.declarators:
                    var = Variable(
                        declarators.type.name,
                        declarator.name,
                        statement.position.line,
                        self.end_line - 1,
                    )
                    lvt[var.name] = var

        for _, reference in javalang_method.filter(jt.MemberReference):
            if reference.member in lvt:
                lvt[reference.member].life_end = reference.position.line

        self.variables = list(lvt.values())
        self.interference_matrix = self.__build_interference_matrix()

    def __build_interference_matrix(self) -> defaultdict[str, dict[str, bool]]:
        """Creates a intereference matrix for a variable list as a nested dictionary"""
        matrix: defaultdict[str, dict[str, bool]] = defaultdict(dict)
        for var1 in self.variables:
            for var2 in self.variables:
                matrix[var1.name][var2.name] = Variable.interfere(var1, var2)

        return matrix


class JavaClass:
    def __init__(self, javalang_class: jt.ClassDeclaration) -> None:
        self.name: str = javalang_class.name
        self.methods: list[JavaMethod] = []
        self.inner_classes: list[JavaClass] = []

        for statement in javalang_class.body:
            if isinstance(statement, jt.MethodDeclaration):
                self.methods.append(JavaMethod(statement))
            elif isinstance(statement, jt.ClassDeclaration):
                self.inner_classes.append(JavaClass(statement))


class JavaCode:
    def __init__(self, code: str) -> None:
        self.code: str = code
        self.classes: list[JavaClass] = []

        ast = javalang.parse.parse(code)
        for node in ast.types:
            if isinstance(node, jt.ClassDeclaration):
                self.classes.append(JavaClass(node))

    def get_snippet(self, start_line: int, end_line: int) -> str:
        return "\n".join(self.code.splitlines()[start_line:end_line])
