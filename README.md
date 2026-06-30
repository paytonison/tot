# tot

tot is a small AI framework being built close to the machine.

It is an experiment in building transformer systems from first principles, with the model core in C and the surrounding tools kept simple enough to understand.

The goal is not to wrap the work in abstractions. The goal is to expose it.

## Purpose

Modern machine learning systems are often large enough that the implementation disappears behind the interface.

tot is written in the other direction.

The framework is concerned with storage, layout, movement, arithmetic, masking, token streams, and the small decisions that become a model. It is meant to make those decisions visible.

A model is not magic.

It is memory and computation arranged carefully.

## Current State

tot is experimental and early.

At this stage, this branch is a project seed: a license, a README, and a clear direction for the system that will be built here.

The implementation, build system, test harness, and example programs are expected to land incrementally. Until those files exist in the repository, this README should describe the intended architecture without pretending that unfinished commands or directories already work.

The project is a workshop, not a product.

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

## Scope

The first implementation work is focused on the machinery needed for small transformer models.

That means token streams, tensor storage, shape handling, masks, attention, feed-forward layers, training loops, tests, and comparison code.

The eventual direction includes decoder-only models, encoder-decoder models, and mixture-of-experts variants.

The first target is not scale.

The first target is understanding.

## Planned Layout

The repository is expected to remain small and plain.

This is the intended shape of the project as the implementation lands:

```text
tot/
├── c/         # model core
├── cpp/       # tokenizer and text tools
├── python/    # experiments and scripts
├── data/      # local data
├── examples/  # small programs
├── tests/     # checks
└── docs/      # notes
```

This layout may change as the system becomes clearer. The tree above is a plan, not a claim that every directory already exists on this branch.

## Building

No build system is committed yet on this branch.

When the C, C++, and Python pieces land, this section should contain exact commands that match the files in the repository. Until then, build instructions should stay honest and avoid placeholder commands that do not run.

Expected future build surfaces:

- C components should build with a small Makefile or equivalent plain command.
- C++ text tools should build with a small CMake project or direct compiler command.
- Python tools should avoid unnecessary dependencies unless a dependency earns its place.

## Testing

No test harness is committed yet on this branch.

Tests should be small and exact. They should check things such as shape rules, buffer sizes, strides, masks, token round trips, deterministic behavior, and numerical sanity.

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

tot is licensed under the MIT License. See `LICENSE`.
