from .ICs import IC


class Manager:
    node_relations: dict[int, int] = {}
    node_values: dict[int, int] = {}

    counter: int = 0

    @classmethod
    def get_nodes(
        cls, input_count: int, output_count: int
    ) -> tuple[list[int], list[int]]:
        input_nodes: list[int] = []
        for _ in range(input_count):
            Manager.counter += 1
            input_nodes.append(Manager.counter)
            cls.node_values.update({Manager.counter: 0})

        output_nodes: list[int] = []
        for _ in range(output_count):
            Manager.counter += 1
            output_nodes.append(Manager.counter)
            cls.node_values.update({Manager.counter: 0})

        return (input_nodes, output_nodes)

    def set_node_relations(
        self, other1: "IC", other2: "IC", node_index_output: int, node_index_input: int
    ):
        for _ in range(other1.no_of_inputs):
            self.node_relations.update(
                {
                    other2.output_nodes[node_index_output]: other1.input_nodes[
                        node_index_input
                    ]
                }
            )

    def create_ic(
        self, ic: str
    ):  # Its been given string for now, idk how we gonna implement the gui
        pass
