from typing import Text

from flowter import Flow, Node


def test_flow_condition():
    def wait_cashier_say(user_name: Text) -> Text:
        msg = f"Hi {user_name}! What do you want to eat?"
        print("Chat Started!")
        print(f"cashier: {msg}")
        return msg

    def wait_user_say(user_say: Text, *kwargs) -> Text:
        msg = f"Hi! I want a {user_say}!"
        print(f"user: {msg}")
        return msg

    def is_burger(user_say: Text) -> bool:
        return "burger" in user_say.casefold()

    def is_pizza(user_say: Text) -> bool:
        return "pizza" in user_say.casefold()

    def give_user_a_burger() -> Text:
        msg = "Here is your burger!"
        print(f"cashier: {msg}")
        return msg

    def give_user_a_pizza() -> Text:
        msg = "Here is your pizza!"
        print(f"cashier: {msg}")
        return msg

    flow = Flow()
    node_1 = Node(wait_cashier_say, return_envelope="cashier_say")
    node_2 = Node(wait_user_say, return_envelope="user_say")
    node_3 = Node(give_user_a_burger, return_envelope="cashier_response")
    node_4 = Node(give_user_a_pizza, return_envelope="cashier_response")

    assert node_1 == flow.add_node(node_1, src=flow.start_node)
    assert node_2 == flow.add_node(node_2, src=node_1)
    assert node_3 == flow.add_node(node_3, src=node_2)
    assert node_3 == flow.add_node(
        node_3, src=node_2, src_condition_node=is_burger, dst=flow.end_node
    )
    assert node_4 == flow.add_node(
        node_4, src=node_2, src_condition_node=is_pizza, dst=flow.end_node
    )

    result = flow.run(user_name="John", user_say="I want a burger!")
    assert result
    assert "burger" in result["cashier_response"].casefold()
