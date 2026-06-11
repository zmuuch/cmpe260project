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


class Block:
    def __init__(self, statements, final_expr):
        self.statements = statements
        self.final_expr = final_expr


class IntLit:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"IntLit({self.value})"


class BoolLit:
    def __init__(self, value):
        self.value = value


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


class AssignStmt:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class PrintStmt:
    def __init__(self, expr):
        self.expr = expr


class IfExpr:
    def __init__(self, cond, then_branch, else_branch):
        self.cond = cond
        self.then_branch = then_branch
        self.else_branch = else_branch


class FunExpr:
    def __init__(self, params, body):
        self.params = params
        self.body = body


class CallExpr:
    def __init__(self, func, args):
        self.func = func
        self.args = args


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
        return self.parse_expression() #temporary without blocks

    def parse_block(self):
        pass

    def parse_statement(self):
        pass

    def parse_expression(self):
        return self.parse_or()

    # precedence chain

    def parse_comparison(self):
        return self.parse_add()

    def parse_and(self):
        return self.parse_comparison()

    def parse_or(self):
        return self.parse_and()

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

    def parse_call(self):
        return self.parse_primary()

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

            value = self.eval(node.value, env)
            env.define(node.name, value)

            return None

        elif isinstance(node, AssignStmt):

            value = self.eval(node.value, env)
            env.update(node.name, value)

            return None

        elif isinstance(node, PrintStmt):

            value = self.eval(node.expr, env)
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

        elif isinstance(node, CallExpr):

            closure = self.eval(node.func, env)

            new_env = Environment(closure.env)

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
        pass

    def eval_unary(self, node, env):
        pass


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

        print(ast)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()

