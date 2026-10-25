from core.components.not_component import OneInputNotComponent


def test_one_input_not_component():
    comp = OneInputNotComponent()
    comp.init_nodes([0], [1])

    for i in range(2):
        output = comp.evaluate({
            0: i,
        })
        assert output[1] == int(not bool(i))
