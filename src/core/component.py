class Component:
    def __init__(self, name: str, input_nodes_count: int, output_nodes_count: int) -> None:
        self.name = name
        self.input_nodes_count = input_nodes_count
        self.output_nodes_count = output_nodes_count

        self.input_nodes: list[int] = []
        self.output_nodes: list[int] = []

    def init_nodes(self, input_nodes: list[int], output_nodes: list[int]):
        self.input_nodes = input_nodes
        self.output_nodes = output_nodes

    def evaluate(self, input_node_values: dict[int, int]) -> dict[int, int]:
        raise Exception("Didn't override evalute function of parent class")
