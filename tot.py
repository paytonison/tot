
#!/usr/bin/env python3
"""
Tot: a tiny total-language prototype.

Tot does not solve the halting problem. It avoids it by accepting only programs
whose termination can be proven by a conservative checker. Programs classified as
Unknown or DoesNotHalt are rejected.

Language sketch:
  - Nat-only values
  - bounded for loops
  - while loops only with a visible `decreases x` countdown proof
  - recursion only with a declared decreasing Nat parameter
  - function calls only to total functions, or self-recursive decreasing calls

Run:
  python tot.py
  python tot.py your_program.tot
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple
import sys


# -----------------------------
# Lexer
# -----------------------------

@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: int


KEYWORDS = {
    "fn", "Nat", "let", "return", "for", "in", "while", "decreases",
    "if", "else", "true", "false",
}

MULTI = ("->", "..", "==", "!=", "<=", ">=", "&&", "||")
SINGLE = set("{}()[];,:=+-*/<>")

def lex(source: str) -> List[Token]:
    out: List[Token] = []
    i = 0
    n = len(source)

    while i < n:
        c = source[i]

        if c.isspace():
            i += 1
            continue

        if source.startswith("//", i):
            j = source.find("\n", i)
            if j == -1:
                break
            i = j + 1
            continue

        if c.isdigit():
            j = i + 1
            while j < n and source[j].isdigit():
                j += 1
            out.append(Token("NUMBER", source[i:j], i))
            i = j
            continue

        if c.isalpha() or c == "_":
            j = i + 1
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            value = source[i:j]
            out.append(Token("IDENT", value, i))
            i = j
            continue

        matched = False
        for op in MULTI:
            if source.startswith(op, i):
                out.append(Token("SYMBOL", op, i))
                i += len(op)
                matched = True
                break
        if matched:
            continue

        if c in SINGLE:
            out.append(Token("SYMBOL", c, i))
            i += 1
            continue

        raise SyntaxError(f"Unexpected character {c!r} at position {i}")

    out.append(Token("EOF", "", n))
    return out


# -----------------------------
# AST
# -----------------------------

class Expr:
    pass

@dataclass(frozen=True)
class IntLit(Expr):
    value: int

@dataclass(frozen=True)
class BoolLit(Expr):
    value: bool

@dataclass(frozen=True)
class Var(Expr):
    name: str

@dataclass(frozen=True)
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass(frozen=True)
class Call(Expr):
    name: str
    args: List[Expr]


class Stmt:
    pass

@dataclass(frozen=True)
class Let(Stmt):
    name: str
    expr: Expr

@dataclass(frozen=True)
class Assign(Stmt):
    name: str
    expr: Expr

@dataclass(frozen=True)
class Return(Stmt):
    expr: Expr

@dataclass(frozen=True)
class For(Stmt):
    var: str
    start: Expr
    end: Expr
    body: List[Stmt]

@dataclass(frozen=True)
class While(Stmt):
    cond: Expr
    decreases: Optional[str]
    body: List[Stmt]

@dataclass(frozen=True)
class If(Stmt):
    cond: Expr
    then_body: List[Stmt]
    else_body: List[Stmt]

@dataclass(frozen=True)
class Function:
    name: str
    params: List[str]
    decreases: Optional[str]
    body: List[Stmt]

@dataclass(frozen=True)
class Program:
    functions: Dict[str, Function]


# -----------------------------
# Parser
# -----------------------------

class Parser:
    def __init__(self, tokens: Sequence[Token]):
        self.tokens = list(tokens)
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def at(self, value: str) -> bool:
        return self.peek().value == value

    def advance(self) -> Token:
        tok = self.peek()
        self.i += 1
        return tok

    def expect(self, value: str) -> Token:
        tok = self.peek()
        if tok.value != value:
            raise SyntaxError(f"Expected {value!r}, got {tok.value!r} at position {tok.pos}")
        return self.advance()

    def expect_ident(self) -> str:
        tok = self.peek()
        if tok.kind != "IDENT" or tok.value in KEYWORDS:
            raise SyntaxError(f"Expected identifier, got {tok.value!r} at position {tok.pos}")
        self.advance()
        return tok.value

    def parse_program(self) -> Program:
        functions: Dict[str, Function] = {}
        while self.peek().kind != "EOF":
            f = self.parse_function()
            if f.name in functions:
                raise SyntaxError(f"Duplicate function {f.name!r}")
            functions[f.name] = f
        return Program(functions)

    def parse_function(self) -> Function:
        self.expect("fn")
        name = self.expect_ident()
        self.expect("(")

        params: List[str] = []
        if not self.at(")"):
            while True:
                param = self.expect_ident()
                self.expect(":")
                self.expect("Nat")
                params.append(param)
                if self.at(","):
                    self.advance()
                    continue
                break

        self.expect(")")
        self.expect("->")
        self.expect("Nat")

        decreases: Optional[str] = None
        if self.at("decreases"):
            self.advance()
            decreases = self.expect_ident()
            if decreases not in params:
                raise SyntaxError(f"decreases parameter {decreases!r} is not a parameter of {name!r}")

        body = self.parse_block()
        return Function(name, params, decreases, body)

    def parse_block(self) -> List[Stmt]:
        self.expect("{")
        body: List[Stmt] = []
        while not self.at("}"):
            if self.peek().kind == "EOF":
                raise SyntaxError("Unclosed block")
            body.append(self.parse_stmt())
        self.expect("}")
        return body

    def parse_stmt(self) -> Stmt:
        if self.at("let"):
            self.advance()
            name = self.expect_ident()
            self.expect(":")
            self.expect("Nat")
            self.expect("=")
            expr = self.parse_expr()
            self.expect(";")
            return Let(name, expr)

        if self.at("return"):
            self.advance()
            expr = self.parse_expr()
            self.expect(";")
            return Return(expr)

        if self.at("for"):
            self.advance()
            var = self.expect_ident()
            self.expect("in")
            start = self.parse_expr()
            self.expect("..")
            end = self.parse_expr()
            body = self.parse_block()
            return For(var, start, end, body)

        if self.at("while"):
            self.advance()
            cond = self.parse_expr()
            decreases: Optional[str] = None
            if self.at("decreases"):
                self.advance()
                decreases = self.expect_ident()
            body = self.parse_block()
            return While(cond, decreases, body)

        if self.at("if"):
            self.advance()
            cond = self.parse_expr()
            then_body = self.parse_block()
            else_body: List[Stmt] = []
            if self.at("else"):
                self.advance()
                else_body = self.parse_block()
            return If(cond, then_body, else_body)

        # assignment
        name = self.expect_ident()
        self.expect("=")
        expr = self.parse_expr()
        self.expect(";")
        return Assign(name, expr)

    def parse_expr(self) -> Expr:
        return self.parse_or()

    def parse_or(self) -> Expr:
        expr = self.parse_and()
        while self.at("||"):
            op = self.advance().value
            right = self.parse_and()
            expr = BinOp(op, expr, right)
        return expr

    def parse_and(self) -> Expr:
        expr = self.parse_equality()
        while self.at("&&"):
            op = self.advance().value
            right = self.parse_equality()
            expr = BinOp(op, expr, right)
        return expr

    def parse_equality(self) -> Expr:
        expr = self.parse_comparison()
        while self.at("==") or self.at("!="):
            op = self.advance().value
            right = self.parse_comparison()
            expr = BinOp(op, expr, right)
        return expr

    def parse_comparison(self) -> Expr:
        expr = self.parse_add()
        while self.at("<") or self.at(">") or self.at("<=") or self.at(">="):
            op = self.advance().value
            right = self.parse_add()
            expr = BinOp(op, expr, right)
        return expr

    def parse_add(self) -> Expr:
        expr = self.parse_mul()
        while self.at("+") or self.at("-"):
            op = self.advance().value
            right = self.parse_mul()
            expr = BinOp(op, expr, right)
        return expr

    def parse_mul(self) -> Expr:
        expr = self.parse_primary()
        while self.at("*") or self.at("/"):
            op = self.advance().value
            right = self.parse_primary()
            expr = BinOp(op, expr, right)
        return expr

    def parse_primary(self) -> Expr:
        tok = self.peek()

        if tok.kind == "NUMBER":
            self.advance()
            return IntLit(int(tok.value))

        if tok.value == "true":
            self.advance()
            return BoolLit(True)

        if tok.value == "false":
            self.advance()
            return BoolLit(False)

        if tok.kind == "IDENT" and tok.value not in KEYWORDS:
            name = self.advance().value
            if self.at("("):
                self.advance()
                args: List[Expr] = []
                if not self.at(")"):
                    while True:
                        args.append(self.parse_expr())
                        if self.at(","):
                            self.advance()
                            continue
                        break
                self.expect(")")
                return Call(name, args)
            return Var(name)

        if self.at("("):
            self.advance()
            expr = self.parse_expr()
            self.expect(")")
            return expr

        raise SyntaxError(f"Expected expression, got {tok.value!r} at position {tok.pos}")


# -----------------------------
# Termination checker
# -----------------------------

class Verdict(Enum):
    Halts = "Halts"
    DoesNotHalt = "DoesNotHalt"
    Unknown = "Unknown"

@dataclass(frozen=True)
class CheckResult:
    verdict: Verdict
    reason: str = ""


class TerminationChecker:
    def __init__(self, program: Program):
        self.program = program
        self.known_total: set[str] = set()
        self.current: Optional[Function] = None

    def check_all(self) -> Dict[str, CheckResult]:
        # Conservative fixed point: once a function is proven total, callers may use it.
        results: Dict[str, CheckResult] = {
            name: CheckResult(Verdict.Unknown, "not checked yet")
            for name in self.program.functions
        }

        changed = True
        rounds = 0
        while changed and rounds <= len(self.program.functions) + 1:
            changed = False
            rounds += 1

            for name, func in self.program.functions.items():
                result = self.check_function(func)
                results[name] = result

                if result.verdict == Verdict.Halts and name not in self.known_total:
                    self.known_total.add(name)
                    changed = True

        # Final pass with the maximal known_total set.
        return {
            name: self.check_function(func)
            for name, func in self.program.functions.items()
        }

    def check_function(self, func: Function) -> CheckResult:
        old_current = self.current
        self.current = func
        env = set(func.params)

        if func.decreases is not None and func.decreases not in env:
            self.current = old_current
            return CheckResult(Verdict.Unknown, f"unknown decreases variable {func.decreases}")

        result = self.check_block(func.body, env)
        self.current = old_current
        return result

    def check_block(self, body: Sequence[Stmt], env: set[str]) -> CheckResult:
        local_env = set(env)

        for stmt in body:
            result = self.check_stmt(stmt, local_env)
            if isinstance(stmt, Let):
                local_env.add(stmt.name)

            if result.verdict != Verdict.Halts:
                return result

            if self.stmt_guarantees_return(stmt):
                # Later statements are unreachable, so they cannot hurt totality.
                return CheckResult(Verdict.Halts, "returns")

        # Falling off the end is defined as an implicit `return 0;`.
        return CheckResult(Verdict.Halts, "falls through with implicit return 0")

    def check_stmt(self, stmt: Stmt, env: set[str]) -> CheckResult:
        if isinstance(stmt, Let):
            return self.check_expr(stmt.expr, env)

        if isinstance(stmt, Assign):
            if stmt.name not in env:
                return CheckResult(Verdict.Unknown, f"assignment to unknown variable {stmt.name}")
            return self.check_expr(stmt.expr, env)

        if isinstance(stmt, Return):
            return self.check_expr(stmt.expr, env)

        if isinstance(stmt, For):
            start = self.check_expr(stmt.start, env)
            end = self.check_expr(stmt.end, env)
            if start.verdict != Verdict.Halts:
                return start
            if end.verdict != Verdict.Halts:
                return end

            body_env = set(env)
            body_env.add(stmt.var)
            body = self.check_block(stmt.body, body_env)
            if body.verdict == Verdict.Halts:
                return CheckResult(Verdict.Halts, "bounded for-loop")
            return body

        if isinstance(stmt, While):
            cond = self.check_expr(stmt.cond, env)
            if cond.verdict != Verdict.Halts:
                return cond

            body = self.check_block(stmt.body, set(env))
            if body.verdict != Verdict.Halts:
                return body

            if isinstance(stmt.cond, BoolLit) and stmt.cond.value is True:
                if self.block_returns_immediately(stmt.body):
                    return CheckResult(Verdict.Halts, "while true returns on first iteration")
                return CheckResult(Verdict.DoesNotHalt, "obvious while true loop")

            if stmt.decreases is None:
                return CheckResult(Verdict.Unknown, "while loop lacks a decreases proof")

            if stmt.decreases not in env:
                return CheckResult(Verdict.Unknown, f"while decreases unknown variable {stmt.decreases}")

            if not self.condition_is_countdown(stmt.cond, stmt.decreases):
                return CheckResult(
                    Verdict.Unknown,
                    f"while condition is not a recognized countdown on {stmt.decreases}",
                )

            if not self.body_has_direct_decrease(stmt.body, stmt.decreases):
                return CheckResult(
                    Verdict.Unknown,
                    f"while body does not directly decrease {stmt.decreases}",
                )

            return CheckResult(Verdict.Halts, f"while loop decreases {stmt.decreases}")

        if isinstance(stmt, If):
            cond = self.check_expr(stmt.cond, env)
            if cond.verdict != Verdict.Halts:
                return cond

            if isinstance(stmt.cond, BoolLit):
                chosen = stmt.then_body if stmt.cond.value else stmt.else_body
                return self.check_block(chosen, set(env))

            then_result = self.check_block(stmt.then_body, set(env))
            else_result = self.check_block(stmt.else_body, set(env))

            if then_result.verdict == Verdict.Halts and else_result.verdict == Verdict.Halts:
                return CheckResult(Verdict.Halts, "both if branches halt")

            if then_result.verdict == Verdict.DoesNotHalt or else_result.verdict == Verdict.DoesNotHalt:
                return CheckResult(
                    Verdict.Unknown,
                    "conditional has a branch that may not halt",
                )

            return CheckResult(Verdict.Unknown, "conditional branch is unknown")

        raise TypeError(f"Unhandled statement: {stmt!r}")

    def check_expr(self, expr: Expr, env: set[str]) -> CheckResult:
        if isinstance(expr, (IntLit, BoolLit)):
            return CheckResult(Verdict.Halts, "literal")

        if isinstance(expr, Var):
            if expr.name in env:
                return CheckResult(Verdict.Halts, "variable")
            return CheckResult(Verdict.Unknown, f"unknown variable {expr.name}")

        if isinstance(expr, BinOp):
            left = self.check_expr(expr.left, env)
            right = self.check_expr(expr.right, env)
            if left.verdict != Verdict.Halts:
                return left
            if right.verdict != Verdict.Halts:
                return right
            return CheckResult(Verdict.Halts, "primitive operation")

        if isinstance(expr, Call):
            if expr.name not in self.program.functions:
                return CheckResult(Verdict.Unknown, f"unknown function {expr.name}")

            callee = self.program.functions[expr.name]
            if len(expr.args) != len(callee.params):
                return CheckResult(
                    Verdict.Unknown,
                    f"{expr.name} expects {len(callee.params)} args, got {len(expr.args)}",
                )

            for arg in expr.args:
                arg_result = self.check_expr(arg, env)
                if arg_result.verdict != Verdict.Halts:
                    return arg_result

            if self.current is not None and expr.name == self.current.name:
                if self.recursive_call_decreases(expr):
                    return CheckResult(Verdict.Halts, "recursive call decreases")
                return CheckResult(Verdict.Unknown, "recursive call is not visibly decreasing")

            if expr.name in self.known_total:
                return CheckResult(Verdict.Halts, f"call to total function {expr.name}")

            return CheckResult(Verdict.Unknown, f"call to function {expr.name} is not yet proven total")

        raise TypeError(f"Unhandled expression: {expr!r}")

    def recursive_call_decreases(self, call: Call) -> bool:
        assert self.current is not None
        func = self.current
        if func.decreases is None:
            return False

        try:
            idx = func.params.index(func.decreases)
        except ValueError:
            return False

        return self.expr_is_strict_decrease(call.args[idx], func.decreases)

    @staticmethod
    def expr_is_strict_decrease(expr: Expr, var: str) -> bool:
        # Recognizes `var - positive_integer`.
        return (
            isinstance(expr, BinOp)
            and expr.op == "-"
            and isinstance(expr.left, Var)
            and expr.left.name == var
            and isinstance(expr.right, IntLit)
            and expr.right.value > 0
        )

    @staticmethod
    def condition_is_countdown(cond: Expr, var: str) -> bool:
        # Recognizes `x > 0`, `x != 0`, `0 < x`, `x >= 1`, and `1 <= x`.
        if not isinstance(cond, BinOp):
            return False

        left, right = cond.left, cond.right

        if isinstance(left, Var) and left.name == var and isinstance(right, IntLit):
            return (
                (cond.op == ">" and right.value == 0)
                or (cond.op == "!=" and right.value == 0)
                or (cond.op == ">=" and right.value >= 1)
            )

        if isinstance(right, Var) and right.name == var and isinstance(left, IntLit):
            return (
                (cond.op == "<" and left.value == 0)
                or (cond.op == "!=" and left.value == 0)
                or (cond.op == "<=" and left.value >= 1)
            )

        return False

    @staticmethod
    def body_has_direct_decrease(body: Sequence[Stmt], var: str) -> bool:
        # Deliberately strict: the decrease must appear directly in the loop body,
        # not hidden behind an if, call, or nested loop.
        for stmt in body:
            if isinstance(stmt, Assign) and stmt.name == var:
                if TerminationChecker.expr_is_strict_decrease(stmt.expr, var):
                    return True
        return False

    @staticmethod
    def block_returns_immediately(body: Sequence[Stmt]) -> bool:
        if not body:
            return False
        return TerminationChecker.stmt_guarantees_return(body[0])

    @staticmethod
    def block_guarantees_return(body: Sequence[Stmt]) -> bool:
        for stmt in body:
            if TerminationChecker.stmt_guarantees_return(stmt):
                return True
        return False

    @staticmethod
    def stmt_guarantees_return(stmt: Stmt) -> bool:
        if isinstance(stmt, Return):
            return True
        if isinstance(stmt, If):
            return (
                TerminationChecker.block_guarantees_return(stmt.then_body)
                and TerminationChecker.block_guarantees_return(stmt.else_body)
            )
        if isinstance(stmt, While):
            return (
                isinstance(stmt.cond, BoolLit)
                and stmt.cond.value is True
                and TerminationChecker.block_returns_immediately(stmt.body)
            )
        return False


# -----------------------------
# Interpreter for accepted Tot
# -----------------------------

class ReturnSignal(Exception):
    def __init__(self, value: int):
        self.value = value


class Interpreter:
    def __init__(self, program: Program):
        self.program = program
        self.steps = 0
        self.max_steps = 100_000

    def call(self, name: str, args: Sequence[int]) -> int:
        if name not in self.program.functions:
            raise RuntimeError(f"Unknown function {name}")
        func = self.program.functions[name]
        if len(args) != len(func.params):
            raise RuntimeError(f"{name} expects {len(func.params)} args, got {len(args)}")
        env = {p: max(0, int(v)) for p, v in zip(func.params, args)}
        try:
            self.exec_block(func.body, env)
        except ReturnSignal as r:
            return max(0, int(r.value))
        return 0

    def tick(self) -> None:
        self.steps += 1
        if self.steps > self.max_steps:
            raise RuntimeError("interpreter step limit exceeded")

    def exec_block(self, body: Sequence[Stmt], env: Dict[str, int]) -> None:
        for stmt in body:
            self.tick()
            self.exec_stmt(stmt, env)

    def exec_stmt(self, stmt: Stmt, env: Dict[str, int]) -> None:
        if isinstance(stmt, Let):
            env[stmt.name] = self.eval_expr(stmt.expr, env)
            return

        if isinstance(stmt, Assign):
            if stmt.name not in env:
                raise RuntimeError(f"Assignment to unknown variable {stmt.name}")
            env[stmt.name] = self.eval_expr(stmt.expr, env)
            return

        if isinstance(stmt, Return):
            raise ReturnSignal(self.eval_expr(stmt.expr, env))

        if isinstance(stmt, For):
            start = self.eval_expr(stmt.start, env)
            end = self.eval_expr(stmt.end, env)
            old = env.get(stmt.var)
            for i in range(start, end):
                env[stmt.var] = i
                self.exec_block(stmt.body, env)
            if old is None:
                env.pop(stmt.var, None)
            else:
                env[stmt.var] = old
            return

        if isinstance(stmt, While):
            while truthy(self.eval_expr(stmt.cond, env)):
                self.exec_block(stmt.body, env)
            return

        if isinstance(stmt, If):
            if truthy(self.eval_expr(stmt.cond, env)):
                self.exec_block(stmt.then_body, env)
            else:
                self.exec_block(stmt.else_body, env)
            return

        raise TypeError(f"Unhandled statement: {stmt!r}")

    def eval_expr(self, expr: Expr, env: Dict[str, int]) -> int | bool:
        if isinstance(expr, IntLit):
            return expr.value

        if isinstance(expr, BoolLit):
            return expr.value

        if isinstance(expr, Var):
            if expr.name not in env:
                raise RuntimeError(f"Unknown variable {expr.name}")
            return env[expr.name]

        if isinstance(expr, Call):
            args = [int(self.eval_expr(arg, env)) for arg in expr.args]
            return self.call(expr.name, args)

        if isinstance(expr, BinOp):
            a = self.eval_expr(expr.left, env)
            b = self.eval_expr(expr.right, env)

            if expr.op == "+":
                return int(a) + int(b)
            if expr.op == "-":
                return max(0, int(a) - int(b))
            if expr.op == "*":
                return int(a) * int(b)
            if expr.op == "/":
                if int(b) == 0:
                    return 0
                return int(a) // int(b)
            if expr.op == "==":
                return a == b
            if expr.op == "!=":
                return a != b
            if expr.op == "<":
                return int(a) < int(b)
            if expr.op == ">":
                return int(a) > int(b)
            if expr.op == "<=":
                return int(a) <= int(b)
            if expr.op == ">=":
                return int(a) >= int(b)
            if expr.op == "&&":
                return truthy(a) and truthy(b)
            if expr.op == "||":
                return truthy(a) or truthy(b)

        raise TypeError(f"Unhandled expression: {expr!r}")


def truthy(value: int | bool) -> bool:
    return bool(value)


# -----------------------------
# Public helpers / CLI
# -----------------------------

def parse_source(source: str) -> Program:
    return Parser(lex(source)).parse_program()

def analyze_source(source: str) -> Tuple[Program, Dict[str, CheckResult]]:
    program = parse_source(source)
    checker = TerminationChecker(program)
    results = checker.check_all()
    return program, results

def accepted(results: Dict[str, CheckResult]) -> bool:
    return all(r.verdict == Verdict.Halts for r in results.values())

def print_results(results: Dict[str, CheckResult]) -> None:
    for name, result in results.items():
        detail = f" — {result.reason}" if result.reason else ""
        print(f"{name}: {result.verdict.value}{detail}")

EXAMPLES: Dict[str, str] = {
    "good_sum_to": """
fn sum_to(n: Nat) -> Nat {
    let acc: Nat = 0;

    for i in 0..n {
        acc = acc + i;
    }

    return acc;
}

fn main() -> Nat {
    return sum_to(5);
}
""",

    "good_factorial": """
fn factorial(n: Nat) -> Nat decreases n {
    if n == 0 {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

fn main() -> Nat {
    return factorial(5);
}
""",

    "good_countdown_while": """
fn countdown(n: Nat) -> Nat {
    while n > 0 decreases n {
        n = n - 1;
    }

    return n;
}

fn main() -> Nat {
    return countdown(100);
}
""",

    "bad_obvious_loop": """
fn doom() -> Nat {
    while true {
    }

    return 0;
}
""",

    "bad_unknown_loop": """
fn maybe(n: Nat) -> Nat {
    while n > 0 {
        n = n - 1;
    }

    return n;
}
""",

    "bad_recursive_growth": """
fn grow(n: Nat) -> Nat decreases n {
    return grow(n + 1);
}
""",
}


def run_examples() -> None:
    for name, source in EXAMPLES.items():
        print(f"\\n=== {name} ===")
        try:
            program, results = analyze_source(source)
            print_results(results)
            if accepted(results) and "main" in program.functions:
                value = Interpreter(program).call("main", [])
                print(f"main() => {value}")
            else:
                print("rejected")
        except Exception as e:
            print(f"error: {e}")


def main(argv: Sequence[str]) -> int:
    if len(argv) == 1:
        run_examples()
        return 0

    path = argv[1]
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    program, results = analyze_source(source)
    print_results(results)

    if not accepted(results):
        print("rejected")
        return 1

    print("accepted")
    if "main" in program.functions:
        value = Interpreter(program).call("main", [])
        print(f"main() => {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
