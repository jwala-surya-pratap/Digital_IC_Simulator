from core.components.or_component import TwoInputOrComponent


def test_two_input_or_component():
    comp = TwoInputOrComponent()
    comp.init_nodes([ 0, 1 ], [2])

    for i in range(2):
        for j in range(2):
            output = comp.evaluate({
                0: i,
                1: j
            })
            assert output[2] == i | j
