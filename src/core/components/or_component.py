from core.component import Component

class TwoInputOrComponent(Component):
    def __init__(self) -> None:
        super().__init__("OR", 2, 1)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        output_value = 0

        if input_node_values[self.input_nodes[0]] == 1 or input_node_values[self.input_nodes[1]] == 1:
            output_value = 1

        return {
            self.output_nodes[0]: output_value
        }
