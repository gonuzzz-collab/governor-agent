# Automation Scripts

These project-local adapters expose the Python stack through four stable GoNucleo interfaces.

## Commands

- scripts/validate runs the strict factory contract when available, locked Ruff checks, and focal tests.
- scripts/doctor performs read-only toolchain diagnostics.
- scripts/test selects focal project tests without installing dependencies.
- scripts/evidence runs validation and diagnostics and emits a gonucleo.evidence.v1 envelope.

## Usage

    ./scripts/doctor
    ./scripts/test
    ./scripts/validate
    ./scripts/evidence --format json
    ./scripts/evidence --mode detail --format json

## Safety contract

- Do not access the network or install dependencies automatically.
- Do not modify host data, runtime, services, or configuration.
- Do not print secrets or include raw command output in evidence.
- Exit 0 for success, 1 for failed checks, and 2 for invalid arguments.

The generated scaffold proves only the automation contract over synthetic code and data. Extend the
adapters when a real workflow exists while preserving these interfaces.
