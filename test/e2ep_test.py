import unittest as ut
from unittest import TestCase
from End2EndPurification.e2ep import BlockingTimes, prepare_nodes_and_links, LocalBellPairProcessor, BellPairProcessor
from End2EndPurification.config import Config

class NodeTest(TestCase):
    def test_connect_to(self):
        pass

class FuncTest(TestCase):
    def test_prepare_nodes_and_links(self):
        c = Config(None)
        for num_node in range(2,5):
            c.num_node = num_node
            nodes, links = prepare_nodes_and_links(c)
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


if __name__ == '__main__':
    ut.main()
