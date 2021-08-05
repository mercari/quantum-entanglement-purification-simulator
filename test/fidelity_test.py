from unittest import TestCase
from End2EndPurification.fidelity import Fidelity
from End2EndPurification.bellpair_processor import Node

class FidelityTest(TestCase):
    def setUp(self) -> None:
        self.fidelity = Fidelity(0.99)
        self.node_left = Node(True, 0.01, 0.02) # p_op, p_mem
        self.node_middle = Node(None, 0.0001, 0.0002)
        self.node_right = Node(False, 0.001, 0.002)
        return super().setUp()
    def test_calc_fidelity_and_blocking_time(self):
        pass
    def test_calc_new_fidelity_by_entanglement_swapping(self):
        fidelity_left = Fidelity(0.98)
        fidelity_right = Fidelity(0.97)
        self.assertEqual(Fidelity.calc_new_fidelity_by_entanglement_swapping(fidelity_left, fidelity_right, self.node_left, self.node_middle, self.node_right).fidelity, 0.98*0.97*0.02*0.0001*0.002)
    def test_calc_new_fidelity_by_purification(self):
        fidelity_left = Fidelity(0.99)
        fidelity_right = Fidelity(0.97)        
        self.assertEqual(Fidelity.calc_new_fidelity_by_purification(fidelity_left, fidelity_right, self.node_left, self.node_right).fidelity, 0.99*0.97 / (0.99 * 0.97 + 0.01 * 0.03)*0.01 * 0.001)
    def test_calc_success_rate_of_purification(self):
        fidelity_left = Fidelity(0.99)
        fidelity_right = Fidelity(0.97)
        self.assertEqual(Fidelity.calc_success_rate_of_purification(fidelity_left, fidelity_right), 0.99*0.97+0.01*0.03)
   

