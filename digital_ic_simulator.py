node_relations = {}
node_values = {}

class IC:
    inputs = []
    outputs = []
    def __init__(self, no_of_inputs, no_of_outputs):
        self.no_of_inputs = no_of_inputs
        self.no_of_outputs = no_of_outputs

    def input_values(self):
        for i in range(self.no_of_inputs):
            entry = int(input(f"Input {i}: "))
            self.inputs.append(entry)


class IC7404(IC):
    def __init__(self, no_of_inputs = 7, no_of_outputs = 7):
        super().__init__(no_of_inputs, no_of_outputs)
    
    def operation(self):
        for i in range(self.no_of_inputs):
            self.outputs.append(not self.inputs[i])

class God():
    