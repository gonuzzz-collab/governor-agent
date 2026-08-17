"""CLI-first product interface for Governor Agent."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from governor_agent.adapters import GovernanceSourceError, SyntheticFactoryAdapter
from governor_agent.agent import AgentConsistencyError, AgentRunResult, GovernorAgentRunner
from governor_agent.agent.provider import create_bedrock_model
from governor_agent.audit import AuditStore
from governor_agent.domain import ChangeRequest, DecisionStatus
from governor_agent.workflow import GovernorWorkflow, WorkflowResult

EXIT_CODES = {
    DecisionStatus.ALLOW: 0,
    DecisionStatus.ALLOW_WITH_CONDITIONS: 0,
    DecisionStatus.ESCALATE: 3,
    DecisionStatus.DENY: 4,
    DecisionStatus.INCOMPLETE_EVIDENCE: 5,
    DecisionStatus.VALIDATION_FAILED: 6,
}
EXPECTED_DEMO = {
    "safe": {DecisionStatus.ALLOW, DecisionStatus.ALLOW_WITH_CONDITIONS},
    "deny": {DecisionStatus.DENY},
    "escalate": {DecisionStatus.ESCALATE},
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="governor",
        description="Govern AI-assisted software changes using explicit authority and evidence.",
    )
    parser.add_argument("--verbose", action="store_true", help="Show validator details.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evaluate = subparsers.add_parser("evaluate", help="Evaluate a structured change request.")
    evaluate.add_argument("request", type=Path)
    evaluate.add_argument("--factory", type=Path, required=True)
    evaluate.add_argument("--audit-dir", type=Path, default=Path(".governor"))
    evaluate.add_argument("--format", choices=("text", "json"), default="text")

    demo = subparsers.add_parser("demo", help="Run a reproducible public scenario.")
    demo.add_argument("scenario", choices=("safe", "deny", "escalate", "all"))
    demo.add_argument(
        "--factory",
        type=Path,
        default=_repo_root() / "fixtures" / "demo_factory",
    )
    demo.add_argument("--audit-dir", type=Path, default=Path(".governor"))
    demo.add_argument("--format", choices=("text", "json"), default="text")

    agent_demo = subparsers.add_parser(
        "agent-demo", help="Run the scenarios through a real Strands Agent tool loop."
    )
    agent_demo.add_argument("scenario", choices=("safe", "deny", "escalate", "all"))
    agent_demo.add_argument(
        "--factory",
        type=Path,
        default=_repo_root() / "fixtures" / "demo_factory",
    )
    agent_demo.add_argument("--audit-dir", type=Path, default=Path(".governor"))
    agent_demo.add_argument("--format", choices=("text", "json"), default="text")
    agent_demo.add_argument("--model", choices=("offline", "bedrock"), default="offline")
    agent_demo.add_argument("--bedrock-model-id")
    agent_demo.add_argument("--aws-region")
    agent_demo.add_argument(
        "--allow-paid-inference",
        action="store_true",
        help="Required acknowledgement before invoking Amazon Bedrock.",
    )
    return parser


def _load_request(path: Path) -> ChangeRequest:
    with path.open("r", encoding="utf-8") as stream:
        return ChangeRequest.model_validate(json.load(stream))


def _run(factory: Path, audit_dir: Path, request_path: Path) -> WorkflowResult:
    source = SyntheticFactoryAdapter(factory)
    workflow = GovernorWorkflow(source, AuditStore(audit_dir))
    return workflow.evaluate(_load_request(request_path))


def _run_agent(
    factory: Path,
    audit_dir: Path,
    request_path: Path,
    *,
    model_name: str,
    model_id: str | None,
    region: str | None,
    allow_paid_inference: bool,
) -> AgentRunResult:
    model = None
    if model_name == "bedrock":
        if not allow_paid_inference:
            raise ValueError("Bedrock requires --allow-paid-inference")
        if model_id is None or region is None:
            raise ValueError("Bedrock requires --bedrock-model-id and --aws-region")
        model = create_bedrock_model(model_id=model_id, region_name=region)
    return GovernorAgentRunner(
        SyntheticFactoryAdapter(factory),
        AuditStore(audit_dir),
        request_path,
        model=model,
    ).run()


def _record_label(result: WorkflowResult, audit_dir: Path) -> str:
    try:
        return result.audit_path.relative_to(audit_dir.resolve()).as_posix()
    except ValueError:
        return result.audit_path.name


def _render_text(result: WorkflowResult, audit_dir: Path, *, verbose: bool) -> None:
    decision = result.decision
    print(f"Governor decision: {decision.status.value}")
    print(f"Request: {decision.request_id}")
    print(f"Reason: {decision.explanation}")
    if decision.violations:
        print("Violations:")
        for violation in decision.violations:
            suffix = f" ({violation.path})" if violation.path else ""
            print(f"  - {violation.code}: {violation.message}{suffix}")
    if decision.human_decisions:
        print("Human decision required:")
        for package in decision.human_decisions:
            print(f"  {package.question}")
            print(f"  Context: {package.context}")
            for option in package.options:
                print(f"  - {option}")
    if verbose and result.validations:
        print("Approved validators:")
        for validation in result.validations:
            print(f"  - {validation.validator_id}: {validation.status.value}")
    print(f"Audit record: {_record_label(result, audit_dir)}")


def _result_payload(result: WorkflowResult, audit_dir: Path) -> dict[str, object]:
    return {
        "decision": result.decision.model_dump(mode="json"),
        "validations": [item.model_dump(mode="json") for item in result.validations],
        "audit_record": _record_label(result, audit_dir),
    }


def _render_json(result: WorkflowResult, audit_dir: Path) -> None:
    print(json.dumps(_result_payload(result, audit_dir), indent=2, sort_keys=True))


def _render_scenarios(
    results: list[tuple[str, WorkflowResult, AgentRunResult | None]],
    audit_dir: Path,
    *,
    output_format: str,
    verbose: bool,
) -> None:
    if output_format == "json":
        payload = []
        for scenario, workflow, agent_result in results:
            item = {"scenario": scenario, **_result_payload(workflow, audit_dir)}
            if agent_result is not None:
                item["agent_report"] = agent_result.report.model_dump(mode="json")
                item["strands_tools"] = list(agent_result.tool_trace)
            payload.append(item)
        print(json.dumps(payload[0] if len(payload) == 1 else payload, indent=2, sort_keys=True))
        return

    for scenario, workflow, agent_result in results:
        if len(results) > 1:
            print(f"\n=== {scenario.upper()} ===")
        _render_text(workflow, audit_dir, verbose=verbose)
        if verbose and agent_result is not None:
            print("Strands tool loop:")
            for name in agent_result.tool_trace:
                print(f"  - {name}")


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "evaluate":
            result = _run(args.factory, args.audit_dir, args.request)
            _render_json(result, args.audit_dir) if args.format == "json" else _render_text(
                result, args.audit_dir, verbose=args.verbose
            )
            return EXIT_CODES[result.decision.status]

        scenarios = tuple(EXPECTED_DEMO) if args.scenario == "all" else (args.scenario,)
        results: list[tuple[str, WorkflowResult, AgentRunResult | None]] = []
        unexpected = False
        for scenario in scenarios:
            request_path = args.factory / "scenarios" / f"{scenario}.json"
            if args.command == "agent-demo":
                agent_result = _run_agent(
                    args.factory,
                    args.audit_dir,
                    request_path,
                    model_name=args.model,
                    model_id=args.bedrock_model_id,
                    region=args.aws_region,
                    allow_paid_inference=args.allow_paid_inference,
                )
                workflow = agent_result.workflow
            else:
                agent_result = None
                workflow = _run(args.factory, args.audit_dir, request_path)
            results.append((scenario, workflow, agent_result))
            unexpected |= workflow.decision.status not in EXPECTED_DEMO[scenario]
        _render_scenarios(
            results,
            args.audit_dir,
            output_format=args.format,
            verbose=args.verbose,
        )
        if len(scenarios) > 1:
            return 1 if unexpected else 0
        return EXIT_CODES[results[0][1].decision.status]
    except (
        OSError,
        ValueError,
        json.JSONDecodeError,
        ValidationError,
        GovernanceSourceError,
        AgentConsistencyError,
    ) as exc:
        print(f"Governor input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
