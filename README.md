# tot

tot is a small AI framework written close to the machine.

It is an experiment in building transformer systems from first principles, with the model core in C and the surrounding tools kept simple enough to understand.

The goal is not to wrap the work in abstractions. The goal is to expose it.

## Purpose

Modern machine learning systems are often large enough that the implementation disappears behind the interface.

tot is written in the other direction.

The framework is concerned with storage, layout, movement, arithmetic, masking, token streams, and the small decisions that become a model. It is meant to make those decisions visible.

A model is not magic.

It is memory and computation arranged carefully.

## Principles

- The core is written in C.
- The code should be direct.
- Data structures should be plain.
- Ownership should be visible.
- Memory layout should be intentional.
- Control flow should be easy to follow.
- Correctness comes before speed.
- Speed comes from understanding.
- A working part should not be rewritten merely to make it look different.

## Boundaries

The system is divided by responsibility:

- C is used for the model core: tensors, buffers, masks, offsets, attention, feed-forward layers, routing, and numerical work.
- C++ is used for text machinery: tokenization, preprocessing, byte handling, and the parts of the system that benefit from stronger string and file abstractions.
- Python is used for experiments: scripts, tests, training runs, comparisons, and automation.

In short:

- _Text belongs to C++._
- _The model belongs to C._
- _Experiments belong to Python._

## Status

tot is experimental.

The interfaces are not stable. The layout may change. Some parts are sketches. Some parts are reference implementations. Some parts exist only to answer one question and then be replaced by something simpler.

This is expected.

The project is a workshop, not a product.

## Scope

The current work is focused on the machinery needed for small transformer models.

This includes token streams, tensor storage, shape handling, masks, attention, feed-forward layers, training loops, tests, and comparison code.

The eventual direction includes decoder-only models, encoder-decoder models, and mixture-of-experts variants.

The first target is not scale.

The first target is understanding.

## Layout

The repository is expected to remain small and plain.

```
tot/
├── c/         # model core
├── cpp/       # tokenizer and text tools
├── python/    # experiments and scripts
├── data/      # local data
├── examples/  # small programs
├── tests/     # checks
└── docs/      # notes
```

This layout may change as the system becomes clearer.

## Building

The build should be ordinary.

For C components:

```sh
make
```

For C++ components:

```sh
cmake -S . -B build
cmake --build build
```

For Python tools:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

These commands may change as the build system settles.

## Testing

Tests should be small and exact.

They should check things such as shape rules, buffer sizes, strides, masks, token round trips, deterministic behavior, and numerical sanity.

```sh
make test
```

For Python tests:

```sh
pytest
```

A test that explains one assumption is better than a large test that hides ten.

## Development

- Inspect first.
- Change the smallest thing that answers the problem.
- Prefer clear code over clever code.
- Prefer explicit state over hidden state.
- Prefer boring interfaces.
- Do not refactor working code without a reason.
- When changing code, say what changed, why it changed, and what was tested.
- When unsure, choose the smaller step.

## Non-goals

- tot is not PyTorch.
- It is not TensorFlow.
- It is not JAX.
- It is not Hugging Face Transformers.
- It is not a production inference server.
- It is not a package of ready-made models.

It is a place to build and inspect the machinery.

## Direction

The long-term goal is a small, understandable framework for transformer research and systems work.

The work begins with plain components.

Then a small model.

Then a correct model.

Then a model that can be changed without fear.

Only after that does performance matter.

## License

No license has been chosen yet.
