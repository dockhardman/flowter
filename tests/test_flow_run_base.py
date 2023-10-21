import random
from typing import List, Text

from flowter import Flow, Node


def test_flow_run_basic_1():
    def read_numbers(length: int = 10, *kwargs) -> List[float]:
        return random.sample(range(100), length)

    def calc_average(numbers: List[float]) -> float:
        return sum(numbers) / len(numbers)

    def calc_max(numbers: List[float]) -> float:
        return max(numbers)

    def calc_min(numbers: List[float]) -> float:
        return min(numbers)

    def export_report(average: float, max_value: float, min_value: float) -> Text:
        report = ""
        report += f"Average: {average}\n"
        report += f"Maximum: {max_value}\n"
        report += f"Minimum: {min_value}\n"
        return report.strip()

    flow = Flow(start_node=Node(lambda *args, **kwargs: "start", name="start"))
    node_1 = Node(read_numbers, return_envelope="numbers", name="read_numbers")
    node_2 = Node(calc_average, return_envelope="average", name="calc_average")
    node_3 = Node(calc_max, return_envelope="max_value", name="calc_max")
    node_4 = Node(calc_min, return_envelope="min_value", name="calc_min")
    node_5 = Node(export_report, return_envelope="report", name="export_report")

    assert node_1 == flow.add_node(node_1, src=flow.start_node)
    assert node_2 == flow.add_node(node_2, src=node_1)
    assert node_3 == flow.add_node(node_3, src=node_2)
    assert node_4 == flow.add_node(node_4, src=node_3)
    assert node_5 == flow.add_node(node_5, src=node_4, dst=flow.end_node)

    result = flow.run(1, 2, 3, b=4, c="5", d=6, length=20)
    assert result["start"] == "start"
    assert len(result["numbers"]) == 20
    assert result["average"] == sum(result["numbers"]) / len(result["numbers"])
    assert result["max_value"] == max(result["numbers"])
    assert result["min_value"] == min(result["numbers"])
    assert result["report"]
