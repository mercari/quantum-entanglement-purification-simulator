from End2EndPurification.bellpair_processor import Fidelity
from unittest import TestCase

from End2EndPurification.config import Config
from End2EndPurification.e2ep import prepare_nodes_and_links
from End2EndPurification.bellpair_processor import BellPairProcessor, LocalBellPairProcessor
    

class LocalBellPairProcessorTest(TestCase):
    def setUp(self) -> None:
        config = Config(None)
        self.nodes, self.links = prepare_nodes_and_links(config)
        self.local_bpps = []
        for i in range(config.num_node-1):
            local_bpp = LocalBellPairProcessor(self.nodes[i], self.nodes[i+1], self.links[i])
            self.local_bpps.append(local_bpp)
            local_bpp.distance = local_bpp.calc_distance()
        return super().setUp()

    def test_calc_distance(self):
        for local_bpp in self.local_bpps:
            self.assertEqual(local_bpp.calc_distance().distance, 20)


class BellPairProcessorTest(TestCase):
    def setUp(self):
        config = Config(None)
        self.config = config
        self.nodes, self.links = prepare_nodes_and_links(config)
        self.local_bpps = []
        for i in range(config.num_node-1):
            local_bpp = LocalBellPairProcessor(self.nodes[i], self.nodes[i+1], self.links[i])
            self.local_bpps.append(local_bpp)
            local_bpp.distance = local_bpp.calc_distance()
        return super().setUp()
        self.bpp = BellPairProcessor(local_bpp[0], local_bpp[1])

    def test_register_nodes(self):
        for lbpp in self.local_bpps:
            self.assertTrue(lbpp.nodes.__len__(), 2)
        
    def test_calc_distance(self):
        # -> Distance.sum_distances(self.bpp_left.distance, self.bpp_right.distance)
        pass
    def test_process_entanglement_swapping(self):
        # -> self.calc_new_fidelity_by_entanglement_swapping()
        # -> self.calc_new_blocking_time_by_entanglement_swapping()
        pass
    def test_calc_new_fidelity_by_entanglement_swapping(self):
        # -> Fidelity.calc_new_fidelity_by_entanglement_swapping(self.bpp_left.fidelity, self.bpp_right.fidelity, self.nodes[0], self.mid_node, self.nodes[1])
        pass
    def test_calc_new_blocking_time_by_entanglement_swapping(self):
        # -> BlockingTimes.merge_blocking_times(self.bpp_left.blocking_times, self.bpp_right.blocking_times)
        pass
    def test_process_purification(self):
        pass
    def test_calc_new_fidelity_by_purification(self):
        # -> Fidelity.calc_new_fidelity_by_purification(self.fidelity, self.fidelity, self.nodes[0], self.nodes[1])
        pass
    def test_calc_new_blocking_time_by_purification(self):
         for local_bpp in self.local_bpps:
            #new_fidelity = (self.config.fidelity_raw_bellpair**2)/(self.config.fidelity_raw_bellpair**2 + (1-self.config.fidelity_raw_bellpair)**2)
            success_rate = Fidelity.calc_success_rate_of_purification(local_bpp.fidelity, local_bpp.fidelity)
            #self.assertEqual(success_rate, local_bpp.fidelity.calc_success_rate_of_purification(local_bpp.fidelity, local_bpp.fidelity))
            bt = local_bpp.calc_new_blocking_time_by_purification()
            if local_bpp.node_left.is_end_node and local_bpp.node_right.is_end_node:
                self.assertEqual(bt.blocking_time_int_node, 0)
                # (init, purification) * 2 * (left and right) + wait * 2
                self.assertAlmostEqual(bt.blocking_time_end_node, ((local_bpp.node_left.unit_time+local_bpp.node_right.unit_time)*4+local_bpp.distance.transmission_time*2)/success_rate)
            elif local_bpp.node_left.is_end_node:
                # left is end node
                # right is int node
                # (init, purification) * 2 + wait
                self.assertEqual(bt.blocking_time_int_node, (local_bpp.node_right.unit_time * 4 +local_bpp.distance.transmission_time)/success_rate)
                self.assertEqual(bt.blocking_time_end_node, (local_bpp.node_left.unit_time * 4 +local_bpp.distance.transmission_time)/success_rate)
            elif local_bpp.node_right.is_end_node:
                # left is int node
                # right is right node
                self.assertEqual(bt.blocking_time_int_node, (local_bpp.node_left.unit_time * 4 +local_bpp.distance.transmission_time)/success_rate)
                self.assertEqual(bt.blocking_time_end_node, (local_bpp.node_right.unit_time * 4 +local_bpp.distance.transmission_time)/success_rate)
            else:
                # (init, purification) * 2 * (left and right) + wait * 2
                print("lbpp dist", local_bpp.distance.distance)
                print("lbpp trans", local_bpp.distance.transmission_time)
                print("lbpp node left:", local_bpp.node_left.id)
                print("lbpp node right:", local_bpp.node_right.id)
                self.assertAlmostEqual(bt.blocking_time_int_node, ((local_bpp.node_left.unit_time+local_bpp.node_right.unit_time)*4+local_bpp.distance.transmission_time*2)/success_rate)
                self.assertEqual(bt.blocking_time_end_node, 0)
    def test_calc_success_rate_of_purification(self):
        # -> Fidelity.calc_success_rate_of_purification(self.fidelity, self.fidelity)
        pass
    def test_repeat_purification_until_target_fidelity(self):
        pass
