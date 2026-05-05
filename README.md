# Tot

Tot is a tiny experimental total programming language implemented as a
self-contained Python prototype. It accepts only programs whose termination can
be proven by a conservative checker, then interprets the accepted programs.

Tot does not solve the general halting problem. Instead, it avoids the
impossible case by narrowing the language so unknown programs stay outside the
total core.

## Status

- Prototype implementation, not a production language.
- Nat-focused syntax and runtime values.
- No third-party Python dependencies.
- Accepted programs are intended to halt.
- `Unknown` is a rejection result, not a warning.

## Termination Verdicts

| Verdict       | Result   | Meaning                                               |
| ------------- | -------- | ----------------------------------------------------- |
| `Halts`       | Accepted | The checker recognized a termination proof.           |
| `DoesNotHalt` | Rejected | The checker found an obvious non-terminating pattern. |
| `Unknown`     | Rejected | The checker could not prove termination.              |

The core rule is simple: only `Halts` programs run.

## Why This Experiment Matters

Tot is more than a toy programming language. It is a compact demonstration of
AI-assisted research, language design, and agentic implementation.

The project began with a discussion about one of the central limits of
computation: the halting problem. Rather than treating the impossible case as a
dead end, the design reframed the problem around total programming: accept only
programs whose termination can be proven, and reject everything else as either
non-halting or unknown.

That idea was then turned into an implementation brief and handed to Codex,
which produced the working Python prototype, including the lexer, parser, AST,
termination checker, interpreter, examples, and `.tot` source convention.

The result is a small but complete artifact: a theoretical computing problem
became a language-design concept, then a working executable prototype.

This matters because it demonstrates the new shape of software creation with
advanced AI systems. The human role was not merely to “prompt” a model. The
human role was to identify the problem, frame the constraints, guide the design,
evaluate the result, and turn the output into a coherent public project.

Tot is intentionally small. That is the point. Its value is not scale. Its value
is compression.

In one tiny repository, it shows:

- theoretical problem framing,
- practical constraint selection,
- programming language design,
- agent delegation,
- implementation synthesis,
- executable validation,
- and public presentation.

Tot is a miniature proof-of-concept for human-directed AI research and
development: abstract computer science converted into working software through a
human/AI cognitive loop.

## Requirements

- Python 3.10 or newer

## Quick Start

Run the built-in examples:

```sh
python3 tot.py
```

Run a Tot source file:

```sh
python3 tot.py path/to/program.tot
```

When every function is proven terminating, Tot prints `accepted`. If the
accepted program contains `main`, the interpreter runs it and prints the return
value.

## Language Features

Tot currently supports:

- `Nat` parameters, local variables, assignments, and return values
- Integer and boolean literals
- Arithmetic operators: `+`, `-`, `*`, `/`
- Comparison operators: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Boolean operators: `&&`, `||`
- `if` / `else` conditionals
- Bounded `for` loops
- Restricted `while` loops with explicit `decreases` hints
- Restricted recursion with a declared decreasing argument
- `//` line comments

All function parameters and return values are declared as `Nat`.

## Termination Model

The checker returns a `Verdict` for each function:

```python
class Verdict(Enum):
    Halts = "Halts"
    DoesNotHalt = "DoesNotHalt"
    Unknown = "Unknown"
```

A program is accepted only when every function receives `Halts`. The checker is
intentionally conservative, so programs that a human can see are terminating may
still be rejected if Tot cannot prove them with its current syntactic rules.

## Examples

### Accepted Bounded Loop

```tot
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
```

This is accepted because the `for` loop has a finite bound.

```text
main() => 10
```

### Accepted Recursive Function

```tot
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
```

This is accepted because the recursive call visibly decreases `n`, which is a
natural number.

```text
main() => 120
```

### Accepted While Loop

```tot
fn countdown(n: Nat) -> Nat {
    while n > 0 decreases n {
        n = n - 1;
    }

    return n;
}

fn main() -> Nat {
    return countdown(100);
}
```

This is accepted because the loop condition is a recognized countdown and the
body directly decreases the declared measure.

```text
main() => 0
```

### Rejected Infinite Loop

```tot
fn doom() -> Nat {
    while true {
    }

    return 0;
}
```

Tot rejects this program as an obvious infinite loop:

```text
doom: DoesNotHalt - obvious while true loop
rejected
```

### Rejected Unknown Loop

```tot
fn maybe(n: Nat) -> Nat {
    while n > 0 {
        n = n - 1;
    }

    return n;
}
```

A human can see that this halts, but Tot currently requires an explicit
`decreases` hint for `while` loops.

```text
maybe: Unknown - while loop lacks a decreases proof
rejected
```

### Rejected Recursive Growth

```tot
fn grow(n: Nat) -> Nat decreases n {
    return grow(n + 1);
}
```

The function claims that `n` is the decreasing measure, but the recursive call
increases it. Tot rejects the program.

```text
grow: Unknown - recursive call is not visibly decreasing
rejected
```

## Checker Rules

Tot v0 recognizes a small set of proof patterns:

- Bounded `for` loops are considered terminating when their bounds terminate.
- `while true` without an immediate guaranteed return is classified as
  `DoesNotHalt`.
- `while` loops need a `decreases` variable.
- Countdown conditions must visibly test the decreasing variable against zero.
- Loop bodies must directly assign `x = x - positive_integer`.
- Recursive functions need a declared `decreases` parameter.
- Recursive calls must pass `x - positive_integer` for that parameter.
- Calls to other functions are allowed only after those functions are proven
  total.

The checker does not perform general theorem proving. It accepts a deliberately
small, syntactic subset.

## Source Layout

```text
.
├── README.md
└── tot.py
```

`tot.py` contains the lexer, parser, AST definitions, termination checker,
interpreter, built-in examples, and command-line entry point.

## Limitations

Tot is not:

- A proof that the halting problem is decidable
- A production programming language
- A complete formal verification system
- A replacement for proof assistants or verification-oriented languages

It is a small prototype demonstrating how a compiler can enforce termination by
refusing to run programs outside a conservative accepted subset.

## Possible Next Steps

- Add a focused test suite and golden files.
- Improve parser and checker error messages.
- Add richer type checking.
- Support richer ranking functions.
- Analyze mutual recursion.
- Add structural recursion over lists or trees.
- Document the termination checker formally.
- Add editor tooling or syntax highlighting.

## License

No license file is currently included.
