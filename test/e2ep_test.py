from unittest import TestCase
from End2EndPurification.e2ep import BlockingTimes, prepare_nodes_and_links, LocalBellPairProcessor

class NodeTest(TestCase):
    def test_connect_to(self):
        pass

class FuncTest(TestCase):
    def test_prepare_nodes_and_links(self):
        fidelity_raw_bellpair = 0.99
        p_int_node = 0.99
        p_end_node = 0.99
        for num_node in range(2,5):
            nodes, links = prepare_nodes_and_links(num_node, fidelity_raw_bellpair, p_int_node, p_end_node)
            self.assertEqual(len(nodes), num_node)
            self.assertEqual(len(links), num_node-1)
            for node in nodes[1:-1]:
                self.assertEqual(len(node.links), 2)
                self.assertEqual(len(node.neighbor), 2)
                self.assertTrue(all([node in n.neighbor for n in node.neighbor]))
            for node in (nodes[0], nodes[-1]):
                self.assertEqual(len(node.links), 1)
                self.assertEqual(len(node.neighbor), 1)
                self.assertTrue(all([node in n.neighbor for n in node.neighbor]))                

class LocalBellPairProcessorTest(TestCase):
    def setUp(self) -> None:
        num_node = 5
        self.p_int_node = 0.99
        self.p_end_node = 0.99        
        self.fidelity_raw_bellpair = 0.98
        target_fidelity = 0.99
        self.nodes, self.links = prepare_nodes_and_links(num_node, self.fidelity_raw_bellpair, self.p_int_node, self.p_end_node)
        self.local_bpps = []
        for i in range(num_node-1):
            local_bpp = LocalBellPairProcessor(self.nodes[i], self.nodes[i+1], self.links[i])
            self.local_bpps.append(local_bpp)
            local_bpp.distance = local_bpp.calc_distance()
        return super().setUp()

    def test_calc_distance(self):
        for local_bpp in self.local_bpps:
            self.assertEqual(local_bpp.calc_distance(), 1)
    def test_calc_new_blocking_time_by_purification(self):
         for local_bpp in self.local_bpps:
            new_fidelity = (self.fidelity_raw_bellpair**2)/(self.fidelity_raw_bellpair**2 + (1-self.fidelity_raw_bellpair)**2)
            success_rate = (self.fidelity_raw_bellpair**2 + (1-self.fidelity_raw_bellpair)**2)
            bt = local_bpp.calc_new_blocking_time_by_purification()
            success_rate 
            if local_bpp.node_left.is_end_node and local_bpp.node_right.is_end_node:
                self.assertEqual(bt.blocking_time_int_node, 0)
                self.assertEqual(bt.blocking_time_end_node, (4+local_bpp.distance*2)/success_rate)
            elif local_bpp.node_left.is_end_node or local_bpp.node_right.is_end_node:              
                self.assertEqual(bt.blocking_time_int_node, (2+local_bpp.distance)/success_rate)
                self.assertEqual(bt.blocking_time_end_node, (2+local_bpp.distance)/success_rate)
            else:
                self.assertEqual(bt.blocking_time_int_node, (4+local_bpp.distance*2)/success_rate)
                self.assertEqual(bt.blocking_time_end_node, 0)
        
  
"""
class BellPairProcessorTest(TestCase):
    def setUp(self):
        self.bpp = main.BellPairProcessor()

    def test_calc_distance(self):

    def test_calc_new_fidelity_by_entanglement_swapping(self):

    def test_calc_new_blocking_time_by_entanglement_swapping(self):
    def test_calc_new_fidelity_by_purification(self):
    def test_calc_new_blocking_time_by_purification(self):
    def test_calc_success_rate_of_purification(self):
    def test_repeat_purification_until_target_fidelity(self):
"""

#if __name__ == '__main__':
#    ut.main()
