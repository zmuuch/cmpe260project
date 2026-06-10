# Azra Zülal Muhcu, 2024400372
# Mustafa Şahin, 2023400162



import sys

# ==================================================
# TOKENS
# ==================================================

class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# ==================================================
# LEXER
# ==================================================

class Lexer:

    def __init__(self, source):
        self.source = source
        self.pos = 0

    def tokenize(self):
        tokens = []

        while self.pos < len(self.source):

            ch = self.source[self.pos]

            if ch.isspace():
                self.pos += 1
                continue

            # TODO:
            # identifiers
            # keywords
            # integers
            # operators
            # punctuation

            raise Exception(f"Unexpected character: {ch}")

        tokens.append(Token("EOF", None))
        return tokens


# ==================================================
# AST NODES
# ==================================================

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


class BoolLit:
    def __init__(self, value):
        self.value = value


class VarExpr:
    def __init__(self, name):
        self.name = name


class BinOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr


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


# ==================================================
# PARSER
# ==================================================

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def eat(self, token_type):
        if self.current().type == token_type:
            self.pos += 1
        else:
            raise Exception(
                f"Expected {token_type}, got {self.current().type}"
            )

    def parse(self):
        block = self.parse_block()
        return Program(block)

    def parse_block(self):
        pass

    def parse_statement(self):
        pass

    def parse_expression(self):
        return self.parse_or()

    # precedence chain

    def parse_or(self):
        pass

    def parse_and(self):
        pass

    def parse_comparison(self):
        pass

    def parse_add(self):
        pass

    def parse_mul(self):
        pass

    def parse_unary(self):
        pass

    def parse_call(self):
        pass

    def parse_primary(self):
        pass


# ==================================================
# ENVIRONMENT
# ==================================================

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


# ==================================================
# CLOSURE
# ==================================================

class Closure:

    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env


# ==================================================
# EVALUATOR
# ==================================================

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


# ==================================================
# MAIN
# ==================================================

def main():

    if len(sys.argv) != 2:
        print(
            "Usage: python interpreter.py program.txt"
        )
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

    evaluator.eval(ast, global_env)


if __name__ == "__main__":
    main()

