from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio

from .. import components as comps


class MemoryDisplay(rio.Component):
    example_state: str = "For demonstration purposes"

    def build(self) -> rio.Component:
        return rio.Text(self.example_state)
