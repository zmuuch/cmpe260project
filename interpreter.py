# Azra Zülal Muhcu, 2024400372
# Mustafa Şahin, 2023400162

import sys

# TOKENS


class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# LEXER

class Lexer:

    def __init__(self, source):
        self.source = source
        self.pos = 0

    def tokenize(self):
        tokens = []

        keywords = {
            "let": "LET",
            "print": "PRINT",
            "if": "IF",
            "then": "THEN",
            "else": "ELSE",
            "end": "END",
            "fun": "FUN",
            "true": "TRUE",
            "false": "FALSE",
            "and": "AND",
            "or": "OR",
            "not": "NOT"
        }

        while self.pos < len(self.source):

            ch = self.source[self.pos]

            # whitespace
            if ch.isspace():
                self.pos += 1
                continue
            
            # comment handling 

            if (
                self.pos + 1 < len(self.source)
                and self.source[self.pos:self.pos+2] == "(*"
            ):

                self.pos += 2

                while (
                    self.pos + 1 < len(self.source)
                    and self.source[self.pos:self.pos+2] != "*)"
                ):
                    self.pos += 1

                if self.pos + 1 >= len(self.source):
                    raise Exception("Unterminated comment")

                self.pos += 2
                continue

            # integers
            if ch.isdigit():

                start = self.pos

                while (
                    self.pos < len(self.source)
                    and self.source[self.pos].isdigit()
                ):
                    self.pos += 1

                value = self.source[start:self.pos]

                tokens.append(
                    Token("INTEGER", int(value))
                )

                continue

            # identifiers / keywords
            if ch.isalpha():

                start = self.pos

                while (
                    self.pos < len(self.source)
                    and (
                        self.source[self.pos].isalnum()
                        or self.source[self.pos] == "_"
                    )
                ):
                    self.pos += 1

                word = self.source[start:self.pos]

                token_type = keywords.get(
                    word,
                    "IDENTIFIER"
                )

                tokens.append(
                    Token(token_type, word)
                )

                continue

            # two-character operators

            if (
                self.pos + 1 < len(self.source)
            ):

                two = self.source[
                    self.pos:self.pos+2
                ]

                two_char = {
                    "==": "EQ",
                    "!=": "NEQ",
                    "<=": "LE",
                    ">=": "GE",
                    "->": "ARROW"
                }

                if two in two_char:

                    tokens.append(
                        Token(
                            two_char[two],
                            two
                        )
                    )

                    self.pos += 2
                    continue

            # one-character tokens

            single = {
                "+": "PLUS",
                "-": "MINUS",
                "*": "STAR",
                "/": "SLASH",
                "=": "ASSIGN",
                "<": "LT",
                ">": "GT",
                "(": "LPAREN",
                ")": "RPAREN",
                ",": "COMMA",
                ";": "SEMICOLON"
            }

            if ch in single:

                tokens.append(
                    Token(
                        single[ch],
                        ch
                    )
                )

                self.pos += 1
                continue

            raise Exception(
                f"Unexpected character: {ch}"
            )

        tokens.append(
            Token("EOF", None)
        )

        return tokens




# AST NODES

class Program:
    def __init__(self, block):
        self.block = block

    def __repr__(self):
        return f"Program({self.block})"


class Block:
    def __init__(self, statements, final_expr):
        self.statements = statements
        self.final_expr = final_expr
    def __repr__(self):
        return f"Block({self.statements}, {self.final_expr})"


class IntLit:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"IntLit({self.value})"


class BoolLit:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"BoolLit({self.value})"


class VarExpr:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VarExpr({self.name})"


class BinOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"


class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

    def __repr__(self):
        return f"UnaryOp({self.op}, {self.expr})"

class LetStmt:
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return f"LetStmt({self.name}, {self.value})"


class AssignStmt:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class PrintStmt:
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"PrintStmt({self.expr})"

class IfExpr:
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return (
            f"IfExpr({self.cond}, "
            f"{self.then_branch}, "
            f"{self.else_branch})"
        )

class ExprStmt:
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"ExprStmt({self.expr})"

class FunExpr:
    def __init__(self, params, body):
        self.params = params
        self.body = body
    def __repr__(self):
        return f"FunExpr({self.params}, {self.body})"


class CallExpr:
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def __repr__(self):
        return f"CallExpr({self.func}, {self.args})"

# PARSER

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def peek(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]

        return Token("EOF", None)

    def eat(self, token_type):
        if self.current().type == token_type:
            self.pos += 1
        else:
            raise Exception(
                f"Expected {token_type}, got {self.current().type}"
            )

    def parse(self):

        block = self.parse_block()

        self.eat("EOF")

        return Program(block)

    def parse_block(self):

        statements = []
        final_expr = None

        while True:

            token = self.current()

            if token.type == "LET":

                stmt = self.parse_statement()
                self.eat("SEMICOLON")
                statements.append(stmt)
                continue

            if token.type == "PRINT":

                stmt = self.parse_statement()
                self.eat("SEMICOLON")
                statements.append(stmt)
                continue

            if (
                token.type == "IDENTIFIER"
                and self.peek().type == "ASSIGN"
            ):

                stmt = self.parse_statement()
                self.eat("SEMICOLON")
                statements.append(stmt)
                continue

            break

        if self.current().type not in (
            "EOF",
            "END",
            "ELSE"
        ):
            final_expr = self.parse_expression()

        return Block(
            statements,
            final_expr
        )
    def parse_statement(self):

        token = self.current()

        # let x = expr

        if token.type == "LET":

            self.eat("LET")

            name = self.current().value

            self.eat("IDENTIFIER")

            self.eat("ASSIGN")

            value = self.parse_expression()

            return LetStmt(name, value)

        # print(expr)

        if token.type == "PRINT":

            self.eat("PRINT")

            self.eat("LPAREN")

            expr = self.parse_expression()

            self.eat("RPAREN")

            return PrintStmt(expr)

        # x = expr

        if (
            token.type == "IDENTIFIER"
            and self.peek().type == "ASSIGN"
        ):

            name = token.value

            self.eat("IDENTIFIER")

            self.eat("ASSIGN")

            value = self.parse_expression()

            return AssignStmt(name, value)

        raise Exception(
            f"Expected statement, got {token.type}"
        )

    def parse_expression(self):
        return self.parse_or()

    # precedence chain

    def parse_comparison(self):

        expr = self.parse_add()

        if self.current().type in (
            "EQ",
            "NEQ",
            "LT",
            "GT",
            "LE",
            "GE"
        ):

            op = self.current().value

            self.eat(self.current().type)

            right = self.parse_add()

            expr = BinOp(
                op,
                expr,
                right
            )

        return expr

    def parse_and(self):

        expr = self.parse_comparison()

        while self.current().type == "AND":

            self.eat("AND")

            right = self.parse_comparison()

            expr = BinOp(
                "and",
                expr,
                right
            )

        return expr
    
    def parse_or(self):

        expr = self.parse_and()

        while self.current().type == "OR":

            self.eat("OR")

            right = self.parse_and()

            expr = BinOp(
                "or",
                expr,
                right
            )

        return expr

    def parse_add(self):

        expr = self.parse_mul()

        while self.current().type in (
            "PLUS",
            "MINUS"
        ):

            op = self.current().value

            self.eat(self.current().type)

            right = self.parse_mul()

            expr = BinOp(
                op,
                expr,
                right
            )

        return expr

    def parse_mul(self):

        expr = self.parse_unary()

        while self.current().type in (
            "STAR",
            "SLASH"
        ):

            op = self.current().value

            self.eat(self.current().type)

            right = self.parse_unary()

            expr = BinOp(
                op,
                expr,
                right
            )

        return expr

    def parse_unary(self):

        token = self.current()

        if token.type == "MINUS":

            self.eat("MINUS")

            return UnaryOp(
                "-",
                self.parse_unary()
            )

        if token.type == "NOT":

            self.eat("NOT")

            return UnaryOp(
                "not",
                self.parse_unary()
            )

        return self.parse_call()
    
    def parse_if(self):

        self.eat("IF")

        cond = self.parse_expression()

        self.eat("THEN")

        then_branch = self.parse_block()

        self.eat("ELSE")

        else_branch = self.parse_block()

        self.eat("END")

        return IfExpr(
            cond,
            then_branch,
            else_branch
        )

    def parse_fun(self):

        self.eat("FUN")

        self.eat("LPAREN")

        params = []

        if self.current().type != "RPAREN":

            params.append(
                self.current().value
            )

            self.eat("IDENTIFIER")

            while self.current().type == "COMMA":

                self.eat("COMMA")

                params.append(
                    self.current().value
                )

                self.eat("IDENTIFIER")

        self.eat("RPAREN")

        self.eat("ARROW")

        body = self.parse_block()

        self.eat("END")

        return FunExpr(
            params,
            body
        )

    def parse_call(self):

        expr = self.parse_primary()

        while self.current().type == "LPAREN":

            self.eat("LPAREN")

            args = []

            if self.current().type != "RPAREN":

                args.append(
                    self.parse_expression()
                )

                while self.current().type == "COMMA":

                    self.eat("COMMA")

                    args.append(
                        self.parse_expression()
                    )

            self.eat("RPAREN")

            expr = CallExpr(
                expr,
                args
            )

        return expr

    def parse_primary(self):
        token = self.current()

        if token.type == "INTEGER":
            self.eat("INTEGER")
            return IntLit(token.value)

        if token.type == "TRUE":
            self.eat("TRUE")
            return BoolLit(True)

        if token.type == "FALSE":
            self.eat("FALSE")
            return BoolLit(False)

        if token.type == "IDENTIFIER":
            self.eat("IDENTIFIER")
            return VarExpr(token.value)

        if token.type == "LPAREN":

            self.eat("LPAREN")

            expr = self.parse_expression()

            self.eat("RPAREN")

            return expr
        
        if token.type == "IF":
            return self.parse_if()

        if token.type == "FUN":
            return self.parse_fun()

        raise Exception(
            f"Unexpected token {token.type}"
        )


# ENVIRONMENT

class Environment:

    def __init__(self, parent=None):
        self.parent = parent
        self.bindings = {}

    def lookup(self, name):

        if name in self.bindings:
            return self.bindings[name]

        if self.parent:
            return self.parent.lookup(name)

        raise Exception(f"Undefined variable: {name}")

    def define(self, name, value):
        self.bindings[name] = value

    def update(self, name, value):

        if name in self.bindings:
            self.bindings[name] = value
            return

        if self.parent:
            self.parent.update(name, value)
            return

        raise Exception(f"Undefined variable: {name}")


# CLOSURE

class Closure:

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env


# EVALUATOR BELOW


class Evaluator:

    def eval(self, node, env):

        if isinstance(node, Program):
            return self.eval(node.block, env)

        elif isinstance(node, Block):

            result = None

            for stmt in node.statements:
                self.eval(stmt, env)

            if node.final_expr:
                result = self.eval(node.final_expr, env)

            return result

        elif isinstance(node, IntLit):
            return node.value

        elif isinstance(node, BoolLit):
            return node.value

        elif isinstance(node, VarExpr):
            return env.lookup(node.name)

        elif isinstance(node, LetStmt):

            if isinstance(node.value, FunExpr):

                env.define(node.name, None)

                closure = Closure(
                    node.value.params,
                    node.value.body,
                    env
                )

                env.update(node.name, closure)

            else:

                value = self.eval(node.value, env)
                env.define(node.name, value)

            return None

        elif isinstance(node, AssignStmt):

            value = self.eval(node.value, env)
            env.update(node.name, value)

            return None
        elif isinstance(node, PrintStmt):

            value = self.eval(node.expr, env)

            if value is True:
                print("true")

            elif value is False:
                print("false")

            elif isinstance(value, Closure):
                print("<function>")

            else:
                print(value)

            return None

        elif isinstance(node, BinOp):
            return self.eval_binop(node, env)

        elif isinstance(node, UnaryOp):
            return self.eval_unary(node, env)

        elif isinstance(node, IfExpr):

            cond = self.eval(node.cond, env)

            if cond:
                return self.eval(node.then_branch, env)
            else:
                return self.eval(node.else_branch, env)

        elif isinstance(node, FunExpr):

            return Closure(
                node.params,
                node.body,
                env
            )
        
        elif isinstance(node, ExprStmt):

            self.eval(node.expr, env)

            return None

        elif isinstance(node, CallExpr):

            closure = self.eval(node.func, env)
            if not isinstance(closure, Closure):
                raise Exception("Attempted to call non-function")

            new_env = Environment(closure.env)
            if len(node.args) != len(closure.params):
                raise Exception(
                    f"Expected {len(closure.params)} arguments, got {len(node.args)}"
                )
            for param, arg in zip(
                closure.params,
                node.args
            ):
                value = self.eval(arg, env)
                new_env.define(param, value)

            return self.eval(
                closure.body,
                new_env
            )

        raise Exception("Unknown AST node")

    def eval_binop(self, node, env):

        left = self.eval(node.left, env)
        right = self.eval(node.right, env)

        if node.op in ("+", "-", "*", "/"):

            if type(left) is not int or type(right) is not int:
                raise Exception(
                    f"Type error: arithmetic requires integers"
                )

        if node.op == "+":
            return left + right

        if node.op == "-":
            return left - right

        if node.op == "*":
            return left * right

        if node.op == "/":

            if right == 0:
                raise Exception("Division by zero")

            return int(left / right)

        if node.op in ("<", ">", "<=", ">="):

            if type(left) is not int or type(right) is not int:
                raise Exception("Type error: comparison requires integers")

        if node.op == "==":
            return left == right

        if node.op == "!=":
            return left != right

        if node.op == "<":
            return left < right

        if node.op == ">":
            return left > right

        if node.op == "<=":
            return left <= right

        if node.op == ">=":
            return left >= right

        if node.op in ("and", "or"):

            if type(left) is not bool or type(right) is not bool:
                raise Exception("Type error: logical operators require booleans")

        if node.op == "and":
            return left and right

        if node.op == "or":
            return left or right

        raise Exception(f"Unknown operator {node.op}")

    def eval_unary(self, node, env):

        value = self.eval(node.expr, env)

        if node.op == "-":

            if type(value) is not int:
                raise Exception(
                    "Type error: unary minus requires integer"
                )

            return -value

        if node.op == "not":

            if type(value) is not bool:
                raise Exception(
                    "Type error: not requires boolean"
                )

            return not value

        raise Exception(f"Unknown unary operator {node.op}")


# MAIN CODE BELOW

def main():
    try:
        if len(sys.argv) != 2:
            sys.exit(1)

        filename = sys.argv[1]

        with open(filename, "r") as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)

        ast = parser.parse()

        global_env = Environment()

        evaluator = Evaluator()

        result = evaluator.eval(
            ast,
            global_env
        )


    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

