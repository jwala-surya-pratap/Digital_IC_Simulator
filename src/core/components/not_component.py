from core.component import Component

class OneInputNotComponent(Component):
    def __init__(self) -> None:
        super().__init__("NOT", 1, 1)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        output_value: int = not input_node_values[self.input_nodes[0]]
        return {
            self.output_nodes[0]: output_value
        }
