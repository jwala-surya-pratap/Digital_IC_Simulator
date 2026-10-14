from core.components.and_component import TwoInputAndComponent
from core.components.or_component import TwoInputOrComponent
from core.manager import ComponentManager


def test_manager():
    manager = ComponentManager()

    node_x = manager.create_node()
    node_y = manager.create_node()
    node_z = manager.create_node()

    manager.set_node_value(node_x, 1)
    manager.set_node_value(node_y, 1)
    manager.set_node_value(node_z, 0)

    comp0 = manager.add_component(TwoInputAndComponent())
    comp1 = manager.add_component(TwoInputOrComponent())

    comp0_inputs = manager.get_component_input_nodes(comp0)
    assert comp0_inputs is not None
    manager.relate_nodes(node_x, comp0_inputs[0])
    manager.relate_nodes(node_x, comp0_inputs[1])

    comp1_inputs = manager.get_component_input_nodes(comp1)
    assert comp1_inputs is not None

    comp0_outputs = manager.get_component_output_nodes(comp0)
    assert comp0_outputs is not None
    manager.relate_nodes(comp0_outputs[0], comp1_inputs[0])
    manager.relate_nodes(node_z, comp1_inputs[1])

    comp1_outputs = manager.get_component_output_nodes(comp1)
    assert comp1_outputs is not None

    manager.evaluate([comp0, comp1])

    assert manager.get_node_value(comp1_outputs[0]) == 1
