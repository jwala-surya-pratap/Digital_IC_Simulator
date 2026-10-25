from core.component import Component

class DisplayComponent(Component):
    def __init__(self) -> None:
        super().__init__("DISP", 1, 0)

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        self.name = f"$>{input_node_values[self.input_nodes[0]]}"
        return {}
