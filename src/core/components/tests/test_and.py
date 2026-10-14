from core.components.and_component import TwoInputAndComponent


def test_two_input_and_component():
    comp = TwoInputAndComponent()
    comp.init_nodes([ 0, 1 ], [2])

    for i in range(2):
        for j in range(2):
            output = comp.evaluate({
                0: i,
                1: j
            })
            assert output[2] == i * j
