no_of_ics:int = 0

class Manager():
    node_relations:dict = {}
    node_values:dict = {}
    
    counter:int = 0

    @staticmethod
    def get_nodes(self, input_count:int, output_count:int) -> tuple[list[int], list[int]] :
        input_nodes:list[int] = []
        for _ in range(input_count):
            Manager.counter += 1
            input_nodes.append(Manager.counter)
            self.node_values.update[{Manager.counter : 0}]

        output_nodes:list[int] = []
        for _ in range(output_count):
            Manager.counter += 1
            input_nodes.append(Manager.counter)
            self.node_values.update[{Manager.counter : 0}]

        return (input_nodes, output_nodes)

    def set_node_relations(self, other1, other2, node_index_output:int, node_index_input:int):
        for i in range(other1.no_of_inputs):
            self.node_relations.update[{other2.output_nodes[node_index_output] : other1.input_nodes[node_index_input]}]

    def create_ic(self, ic):
        pass
    



class IC:

    def __init__(self, no_of_inputs:int, no_of_outputs:int):
        self.no_of_inputs = no_of_inputs
        self.no_of_outputs = no_of_outputs

        no_of_ics += 1

        self.inputs_nodes, self.outputs_nodes = Manager.get_nodes(self.no_of_inputs, self.no_of_outputs)

        self.node_start_value = Manager.counter


    def input_values(self):
        for i in range(self.no_of_inputs):
            entry = int(input(f"Input {i}: "))
            self.inputs.append(entry)

    



class IC7404(IC):
    def __init__(self, no_of_inputs = 7, no_of_outputs = 7):
        super().__init__(no_of_inputs, no_of_outputs)

    
    def evaluate(self):
        for i in range(self.no_of_inputs):
            self.outputs.append(not self.inputs[i])
    

    
