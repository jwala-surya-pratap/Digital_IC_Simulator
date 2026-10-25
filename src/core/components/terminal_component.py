from core.component import Component

class HiTerminalComponent(Component):
    def __init__(self) -> None:
        self.output = 1
        super().__init__("HI", 0, 1)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        return {
            self.output_nodes[0]: self.output
        }

class LoTerminalComponent(Component):
    def __init__(self) -> None:
        self.output = 0
        super().__init__("LO", 0, 1)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        return {
            self.output_nodes[0]: self.output
        }
