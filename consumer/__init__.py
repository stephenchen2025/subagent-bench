"""The frozen consumer: the orchestrator stand-in that reads reports (DESIGN.md 4)."""

from consumer.probe import Probe, ProbeAnswer, Verdict, build_prompt
from consumer.replay import ReplayConsumer

__all__ = ["Probe", "ProbeAnswer", "Verdict", "build_prompt", "ReplayConsumer"]
