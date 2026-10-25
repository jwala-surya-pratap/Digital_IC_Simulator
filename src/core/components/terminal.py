from core.component import Component

class TerminalComponent(Component):
    def __init__(self) -> None:
        self.output = 0
        super().__init__("TERM", 0, 1)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        return {
            self.output_nodes[0]: self.output
        }
