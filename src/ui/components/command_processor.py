from __future__ import annotations

from dataclasses import KW_ONLY, field
from turtle import textinput
import typing as t
from contextlib import redirect_stdout
import io
import rio
from pyforth.runtime import Interpreter, RAM
from .. import components as comps


class CommandProcessor(rio.Component):
    """manage input to the engine"""
    engine:Interpreter
    engine_stack:list[t.Any] = field(default_factory=list)
    memory: t.Optional[RAM]=None
    command_text:str=''
    output_text: str = 'Ouput'


    def filePicked(self, event: rio.FilePickEvent):
        with open(event.file.name, "r", encoding='utf-8') as fd:
            self.command_text =fd.read()

    def run_command(self):
        if self.command_text:
            f = io.StringIO()
            with redirect_stdout(f):
                self.engine.interpret(self.command_text)
            self.output_text = f.getvalue()
            self.engine_stack = self.engine.stack

    def clear_input(self):
        self.command_text = ''

    def clear_output(self):
        self.output_text=''

    def build(self) -> rio.Component:
        return rio.Card(
            rio.Column(
                rio.Row(
                    rio.Button("Clear Output", shape="rectangle", align_x=0, align_y=0.5, on_press=self.clear_output),
                    rio.ScrollContainer(
                        rio.Text(text=self.output_text, grow_y=True, overflow='wrap'),
                        initial_y=5, grow_x=True
                    ),
                    spacing = 0.5
                ),
                rio.Row(
                    rio.Column(rio.Button("Run", shape="rectangle", align_x=0, align_y=0.5, on_press=self.run_command),
                               rio.Button("clear", shape="rectangle", align_x=0, align_y=0.5, on_press=self.clear_input)
                               ),
                    
                    rio.MultiLineTextInput(
                        label="Input",
                        text=self.bind().command_text,
                        # align_x=0.5,
                        auto_adjust_height=False,
                        grow_x=True
                    ),
                        spacing = 0.5
                ),
                rio.Row(
                    # rio.Button("Load", shape="rectangle", align_x=0, align_y=0),
                    rio.FilePickerArea(rio.Text("select a file to load"), on_pick_file=self.filePicked),
                    spacing=0.6,
                ),
                # align_y=0
            ),
        )
