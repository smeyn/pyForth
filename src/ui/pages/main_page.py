from __future__ import annotations

import typing as t
from dataclasses import KW_ONLY, field

import rio
from pyforth.runtime import Interpreter, RAM
from .. import components as comps

@rio.page(url_segment="")
class MainPage(rio.Component):
    engine:Interpreter=Interpreter()
    engine_stack:list[t.Any] = field(default_factory=list)
    # memory: t.Optional[RAM]=None
    

    # def __post_init__(self):
    #     self.engine_stack = self.engine.stack
    #     self.memory = self.engine.mem

    def build(self) -> rio.Component:

        grid=rio.Grid(grow_y=True)
        grid.add(comps.CommandProcessor(
            engine=self.engine, 
            engine_stack=self.bind().engine_stack,
            # memory = self.bind().memory
            ),row=0, column =0, width=3)
        # grid.add(rio.Text("enter command", align_y=0.0), row=0, column =0, width=1)
        # grid.add(rio.TextInput( align_y=0.0), row=0, column =2, width=3)
        grid.add(comps.StackDisplay( 
            self.engine,
            engine_stack=self.bind().engine_stack, 
            # memory = self.bind().memory
            )
                 , row=1, column =0, width = 3)
        grid.add(rio.Column(), row=2, column=0, width=3)
        grid.add(rio.Text("menory"), row=1, column =3, width = 3)
        grid.add(rio.Column(), row=2, column=3, width=3)
        

        col = rio.Column(
            rio.Text("Py Forth", style="heading1"),
            rio.Row(
                rio.Button("Open", shape="rectangle",align_x=1.0),
                rio.Button("Import", shape="rectangle",align_x=1.0),
                rio.Button("Save", shape="rectangle",align_x=1.0),
                rio.Button("Exit", shape="rectangle",align_x=1.0),
                spacing=0.4,
                align_x=0.0
            ),
            grid,
            rio.Row(grow_y=True)
                

        )
        
        return col