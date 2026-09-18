from .manager import Manager

no_of_ics:int = 0

class IC:
    
    def __init__(self, no_of_inputs:int, no_of_outputs:int):
        self.no_of_inputs = no_of_inputs
        self.no_of_outputs = no_of_outputs

        global no_of_ics
        no_of_ics += 1

        self.input_nodes, self.output_nodes = Manager.get_nodes(self.no_of_inputs, self.no_of_outputs)

        self.node_start_value = Manager.counter


    def input_values(self):
        for i in range(self.no_of_inputs):
            entry = int(input(f"Input {i}: "))
            Manager.node_values.update({self.input_nodes[i] : entry})

