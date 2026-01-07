from __future__ import annotations
import javalang
import javalang.tree as jt
from dataclasses import dataclass
from collections import defaultdict


INDENTATION = 4

SCOPES = (
    jt.ForStatement,
    jt.WhileStatement,
    jt.IfStatement,
    jt.CatchClause,
    jt.MethodDeclaration,
)


def rec_get_last_expr_pos(scope) -> int:
    """Get the position of the last expression of a scope recursively"""
    if hasattr(scope, "body"):
        return rec_get_last_expr_pos(scope.body)

    if isinstance(scope, jt.BlockStatement):
        return rec_get_last_expr_pos(scope.statements[-1])

    if isinstance(scope, jt.IfStatement):
        if scope.else_statement:
            return rec_get_last_expr_pos(scope.else_statement)
        else:
            return rec_get_last_expr_pos(scope.then_statement)

    return scope.position.line


@dataclass
class Variable:
    type: str
    name: str
    life_start: int
    life_end: int

    @staticmethod
    def interfere(var1: Variable, var2: Variable) -> bool:
        """Return true if two variables overlap or false otherwise"""
        if not var1.used or not var2.used:
            return False

        return max(var1.life_start, var2.life_start) <= min(
            var1.life_end, var2.life_end
        )

    def used(self) -> bool:
        return self.life_start != self.life_end

    def __str__(self) -> str:
        return f"{self.type} {self.name}: {self.life_start} - {self.life_end}"


class JavaMethod:
    def __init__(self, javalang_method: jt.MethodDeclaration) -> None:
        self.name: str = javalang_method.name
        self.variables: list[Variable] = []
        self.interference_matrix: defaultdict[str, dict[str, bool]]
        self.start_line: int = javalang_method.position.line - 1
        self.end_line: int = javalang_method.body[-1].position.line + 1

        tmp_lvt: dict[str, Variable] = {}

        # Handle method parameters
        for param in javalang_method.parameters:
            tmp_lvt[param.name] = Variable(
                param.type.name, param.name, self.start_line, self.start_line
            )

        # Find variable declarations
        for path, node in javalang_method:
            if isinstance(node, jt.ForControl) and node.init:
                # Handle the for-loop initializer
                variables: list[str] = list(
                    map(lambda d: d.name, node.init.declarators)
                )
                for_statement: jt.ForStatement = path[-1]
                last_expression = for_statement.body
                if isinstance(last_expression, jt.BlockStatement):
                    last_expression = last_expression.statements[-1]

                life_start = for_statement.position.line
                life_end = last_expression.position.line
                for variable in variables:
                    tmp_lvt[variable] = Variable(
                        node.init.type.name, variable, life_start, life_end
                    )
            elif isinstance(node, jt.LocalVariableDeclaration):
                # Handle regular variable declarations
                variables: list[str] = list(map(lambda d: d.name, node.declarators))
                life_start: int = node.position.line
                life_end: int = life_start
                scope = None
                for variable in variables:
                    tmp_lvt[variable] = Variable(
                        node.type.name, variable, life_start, life_end
                    )

        # Get variable references
        for _, reference in javalang_method.filter(jt.MemberReference):
            if reference.member in tmp_lvt:
                tmp_life_end = tmp_lvt[reference.member].life_end
                current_life_end = reference.position.line
                tmp_lvt[reference.member].life_end = max(tmp_life_end, current_life_end)

        self.variables = list(tmp_lvt.values())
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
