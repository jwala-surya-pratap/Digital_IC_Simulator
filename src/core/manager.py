from core.component import Component


class ComponentManager:
    node_count: int = 0
    node_ids: list[int] = []
    node_relations: dict[int, set[int]] = {}
    node_values: dict[int, int] = {}

    components: list[Component] = []
    component_to_inputnodes: dict[int, set[int]] = {}
    component_to_outputnodes: dict[int, set[int]] = {}

    def create_node(self) -> int:
        self.node_count += 1
        self.node_ids.append(self.node_count)
        self.node_values[self.node_count] = 0

        return self.node_count

    def relate_nodes(self, x: int, y: int):
        self.node_relations.setdefault(x, set()).add(y)

    def set_node_value(self, node: int, value: int):
        if node in self.node_values:
            self.node_values[node] = value

    def get_node_value(self, node: int) -> int | None:
        if node in self.node_values:
            return self.node_values[node]

        return None

    def reflect_node_values(self):
        for node, relations in self.node_relations.items():
            value = self.get_node_value(node)
            if value is None:
                raise Exception("During reflection, value if none for node")
            for related_node in relations:
                self.set_node_value(related_node, value)

    def add_component(self, component: Component) -> int:
        component_id = len(self.components)
        input_nodes = [self.create_node() for _ in range(component.input_nodes_count)]
        output_nodes = [self.create_node() for _ in range(component.output_nodes_count)]

        component.init_nodes(input_nodes, output_nodes)
        self.components.append(component)

        self.component_to_inputnodes[component_id] = set(input_nodes)
        self.component_to_outputnodes[component_id] = set(output_nodes)

        return component_id

    def get_component_input_nodes(self, comp_id: int) -> list[int] | None:
        if comp_id < len(self.components):
            return list(self.component_to_inputnodes[comp_id])

        return None

    def get_component_output_nodes(self, comp_id: int) -> list[int] | None:
        if comp_id < len(self.components):
            return list(self.component_to_outputnodes[comp_id])

        return None

    def evaluate(self, eval_order: list[int]):
        print("[EVAL] executing with order:", eval_order)
        print("[EVAL] Invoke reflection before execution")
        self.reflect_node_values()

        print("[EVAL] evaluating...")
        for comp_id in eval_order:
            print("[EVAL] currently evaluating for compid:", comp_id)
            component = self.components[comp_id]

            input_nodes = self.get_component_input_nodes(comp_id)
            if input_nodes is None:
                raise Exception("Tried to retrieve all input node IDs for component, but found None")
            print("[EVAL] Component's input nodes:", input_nodes)

            input_node_dict: dict[int, int] = {}
            for input_node in input_nodes:
                value = self.get_node_value(input_node)
                if value is None:
                    raise Exception("Tried to retrieve value of an input Node, but found None")
                input_node_dict[input_node] = value
            print("[EVAL] Component's input node values:", input_node_dict)

            output_node_values = component.evaluate(input_node_dict)
            print("[EVAL] Component Evaluation output:", output_node_values)

            print("[EVAL] Set output node values")
            for node, value in output_node_values.items():
                self.node_values[node] = value

            print("[EVAL] Invoked reflection")
            self.reflect_node_values()

        print("[EVAL] Done!")
