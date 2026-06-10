"""Supervisor-Workers demo for the Day09 lab assignment.

This version is deterministic so it can run without an API key during grading,
while still using LangGraph's StateGraph and Send API to model the pattern.
"""

from __future__ import annotations

import asyncio
import sys
from dataclasses import dataclass
from operator import add
from typing import Annotated, TypedDict

try:
    from langgraph.constants import Send
    from langgraph.graph import END, StateGraph

    HAS_LANGGRAPH = True
except ModuleNotFoundError:
    HAS_LANGGRAPH = False
    END = "__end__"
    StateGraph = None

    @dataclass(frozen=True)
    class Send:
        """Minimal fallback shape matching LangGraph Send for local dry runs."""

        node: str
        arg: dict


DEFAULT_QUESTION = (
    "A company breached a software contract, hid overseas revenue from tax filings, "
    "and leaked customer personal data. What should management worry about?"
)


class WorkerResult(TypedDict):
    worker: str
    focus: str
    analysis: str
    actions: list[str]


class AssignmentState(TypedDict):
    question: str
    selected_workers: list[str]
    worker_results: Annotated[list[WorkerResult], add]
    final_answer: str


WORKER_KEYWORDS = {
    "contract_worker": [
        "contract",
        "breach",
        "agreement",
        "liability",
        "damages",
        "hop dong",
        "vi pham",
    ],
    "tax_worker": ["tax", "irs", "revenue", "offshore", "thue", "tron thue"],
    "compliance_worker": [
        "compliance",
        "privacy",
        "data",
        "gdpr",
        "regulation",
        "du lieu",
        "ro ri",
    ],
}


def supervisor(state: AssignmentState) -> dict:
    """Choose which workers are needed for the user's question."""
    question_lower = state["question"].lower()
    selected_workers = [
        worker
        for worker, keywords in WORKER_KEYWORDS.items()
        if any(keyword in question_lower for keyword in keywords)
    ]

    if not selected_workers:
        selected_workers = ["contract_worker"]

    return {"selected_workers": selected_workers}


def route_to_workers(state: AssignmentState) -> list[Send]:
    """Dispatch the selected workers in parallel."""
    return [Send(worker, state) for worker in state["selected_workers"]]


def contract_worker(state: AssignmentState) -> dict:
    """Worker for contract and civil-liability analysis."""
    result: WorkerResult = {
        "worker": "contract_worker",
        "focus": "Contract and civil liability",
        "analysis": (
            "The company should assess breach of contract exposure, available remedies, "
            "causation, mitigation, limitation-of-liability clauses, and whether equitable "
            "relief such as injunction or specific performance is possible."
        ),
        "actions": [
            "Review contract remedies, notice, cure periods, and liability caps.",
            "Preserve evidence and quantify direct plus consequential damages.",
        ],
    }
    return {"worker_results": [result]}


def tax_worker(state: AssignmentState) -> dict:
    """Worker for tax-risk analysis."""
    result: WorkerResult = {
        "worker": "tax_worker",
        "focus": "Tax exposure",
        "analysis": (
            "Hidden overseas revenue can create back-tax, interest, civil fraud penalties, "
            "reporting penalties, and possible criminal referral if conduct was willful."
        ),
        "actions": [
            "Reconcile revenue, amended returns, FBAR/FATCA filings, and transfer-pricing records.",
            "Evaluate voluntary disclosure or cooperation strategy before enforcement escalates.",
        ],
    }
    return {"worker_results": [result]}


def compliance_worker(state: AssignmentState) -> dict:
    """Worker for compliance, privacy, and regulatory analysis."""
    result: WorkerResult = {
        "worker": "compliance_worker",
        "focus": "Compliance and privacy",
        "analysis": (
            "A customer-data leak can trigger breach notification, regulator reporting, "
            "privacy-law penalties, customer claims, and governance review. Management should "
            "also assess whether controls, policies, and incident response were adequate."
        ),
        "actions": [
            "Run incident response, notify affected parties where required, and document remediation.",
            "Review privacy notices, consent basis, security controls, and board reporting.",
        ],
    }
    return {"worker_results": [result]}


def aggregator(state: AssignmentState) -> dict:
    """Create the final answer from all worker outputs."""
    sections = []
    for result in state["worker_results"]:
        action_lines = "\n".join(f"  - {action}" for action in result["actions"])
        sections.append(
            f"## {result['focus']}\n"
            f"{result['analysis']}\n\n"
            f"Recommended actions:\n{action_lines}"
        )

    final_answer = (
        "Supervisor-Workers final analysis\n\n"
        f"Question: {state['question']}\n\n"
        + "\n\n".join(sections)
        + "\n\nPriority: preserve evidence, stop ongoing harm, quantify exposure, "
        "and coordinate counsel-led remediation across all selected workstreams."
    )
    return {"final_answer": final_answer}


def build_graph():
    """Build and compile the Supervisor-Workers graph."""
    if not HAS_LANGGRAPH:
        return SimpleSupervisorWorkersGraph()

    graph = StateGraph(AssignmentState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("contract_worker", contract_worker)
    graph.add_node("tax_worker", tax_worker)
    graph.add_node("compliance_worker", compliance_worker)
    graph.add_node("aggregator", aggregator)

    graph.set_entry_point("supervisor")
    graph.add_conditional_edges(
        "supervisor",
        route_to_workers,
        ["contract_worker", "tax_worker", "compliance_worker"],
    )
    graph.add_edge("contract_worker", "aggregator")
    graph.add_edge("tax_worker", "aggregator")
    graph.add_edge("compliance_worker", "aggregator")
    graph.add_edge("aggregator", END)
    return graph.compile()


class SimpleSupervisorWorkersGraph:
    """Fallback runner used only when LangGraph is not installed locally."""

    worker_map = {
        "contract_worker": contract_worker,
        "tax_worker": tax_worker,
        "compliance_worker": compliance_worker,
    }

    async def ainvoke(self, state: AssignmentState) -> AssignmentState:
        current = dict(state)
        current.update(supervisor(current))

        worker_outputs = await asyncio.gather(
            *[
                asyncio.to_thread(self.worker_map[send.node], send.arg)
                for send in route_to_workers(current)
            ]
        )
        worker_results: list[WorkerResult] = []
        for output in worker_outputs:
            worker_results.extend(output["worker_results"])

        current["worker_results"] = worker_results
        current.update(aggregator(current))
        return current


async def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or DEFAULT_QUESTION
    graph = build_graph()
    result = await graph.ainvoke(
        {
            "question": question,
            "selected_workers": [],
            "worker_results": [],
            "final_answer": "",
        }
    )

    print("=" * 72)
    print("LAB ASSIGNMENT: SUPERVISOR-WORKERS AGENT")
    print("=" * 72)
    print(f"Selected workers: {', '.join(result['selected_workers'])}")
    print("-" * 72)
    print(result["final_answer"])


if __name__ == "__main__":
    asyncio.run(main())
