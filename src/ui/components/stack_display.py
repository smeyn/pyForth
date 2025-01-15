from __future__ import annotations

from dataclasses import KW_ONLY, field
import typing as t

import rio
from pyforth.runtime import Interpreter, RAM
from .. import components as comps


class StackDisplay(rio.Component):
    engine:Interpreter
    engine_stack:list[t.Any] = field(default_factory=list)
    # memory: t.Optional[RAM]=None
    table_data:dict[str,list]=field(default_factory=dict)

    def __post_init__(self):

        self.table_data = {
                "Value": [str(item) for item in self.engine_stack],
                "type": [str(type(item)) for item in self.engine_stack],                
            }

    def clear_stack(self):
        self.engine.reset()
        self.engine_stack = self.engine.stack

    def build(self) -> rio.Component:
        table_data = {
                "Value": reversed([str(item) for item in self.engine_stack]),
                "type": reversed([str(type(item)) for item in self.engine_stack]),                
            }
        return rio.Card(
            rio.Column(
                rio.Row(
                    rio.Text("Stack", style="heading3"),
                    rio.Button("Clear Stack", on_press=self.clear_stack,
                               align_x=1),
                    align_y=0
                ),  
                
                rio.Table(
                    data = table_data
                ),
                rio.Text(",".join([str(item) for item in self.engine_stack])),
            )

        )
