import math

try:
    from fidelity import Fidelity, fidelity_to_p, p_to_fidelity
except:
    from End2EndPurification.fidelity import Fidelity, fidelity_to_p, p_to_fidelity

try:
    from blocking_times import BlockingTimes
except:
    from End2EndPurification.blocking_times import BlockingTimes


class Link:
    def __init__(self, fidelity_raw_bellpair) -> None:
        self.fidelity_raw_bellpair = fidelity_raw_bellpair
        self.nodes = []
    def connect(self, node_left, node_right):
        self.nodes.append(node_left)
        self.nodes.append(node_right)

class Node:
    def __init__(self, is_end_node: bool, p_op, p_mem) -> None:
        self.neighbor = []
        self.links = []
        self.is_end_node = is_end_node
        self.p_op = p_op
        self.p_mem = p_mem
    def __repr__(self):
        return "<num_neighbor:" + repr(len(self.neighbor)) + ",is_end_node:" + repr(self.is_end_node) + ">"
    def connect_to(self, neighbor, link) -> None:
        if neighbor in self.neighbor:
            return
        self.neighbor.append(neighbor)
        self.links.append(link)
        neighbor.connect_to(self, link)

class BellPairProcessor:
    def __init__(self, bpp_left, bpp_right) -> None:
        self.bpp_left = bpp_left
        self.bpp_right = bpp_right
        self.fidelity: float = None
        self.blocking_times = None
        self.distance = self.calc_distance()
        
        self.nodes, self.mid_node = self.register_nodes()

       # log for debug
        self.fidelity_repetition_log = []
        self.blocking_time_repetition_log = []
        self.success_rate_repetition_log = []
    def register_nodes(self):
        nodes = []
        for node in self.bpp_left.nodes + self.bpp_right.nodes:
            if node in nodes:
                nodes.remove(node)
                mid_node = node
            else:
                nodes.append(node)
        assert(nodes.__len__() == 2)
        return nodes, node
 
    def calc_distance(self) -> int:
        return self.bpp_left.distance + self.bpp_right.distance
    def process_entanglement_swapping(self):
        # 1 BPP毎に1回しか呼び出されない

        # Respectively,
        # fidelity decrease by E.S. itself 
        # fidelity decrease by operation (gate) error
        # (fidelity decrease by memorying) <- next operation does not need to wait pauli frames of E.S.
        self.fidelity = Fidelity.calc_new_fidelity_by_entanglement_swapping(self.bpp_left.fidelity, self.bpp_right.fidelity, p_to_fidelity(self.mid_node.p_op))
        print(__name__, self.fidelity)
        #(((1-self.nodes[0].p_mem) * (1-self.nodes[1].p_mem))**(self.distance)) * \

        self.blocking_times = self.calc_new_blocking_time_by_entanglement_swapping()
    def calc_new_blocking_time_by_entanglement_swapping(self) -> int:
        btl = BlockingTimes(self.bpp_left.blocking_times.blocking_time_int_node + self.bpp_right.blocking_times.blocking_time_int_node,
                                self.bpp_left.blocking_times.blocking_time_end_node + self.bpp_right.blocking_times.blocking_time_end_node)
        return btl

    def process_purification(self):
        if self.fidelity.fidelity <= 0.5 or self.blocking_times.blocking_time_int_node >= BlockingTimes.LIMIT or self.blocking_times.blocking_time_end_node >= BlockingTimes.LIMIT:
            # fidelity less than 0.5 cannot be improved
            return False
        success_rate = Fidelity.calc_success_rate_of_purification(self.fidelity, self.fidelity)
        
        self.success_rate_repetition_log.append(success_rate)
        self.fidelity_repetition_log.append(self.fidelity)
        self.blocking_time_repetition_log.append(self.blocking_times)

        self.blocking_times = self.calc_new_blocking_time_by_purification()

        # Respectively,
        # fidelity increase by purification  
        # fidelity decrease by operation (gate) error
        print(self.fidelity)
        self.fidelity = Fidelity.calc_new_fidelity_by_purification(self.fidelity, self.fidelity, p_to_fidelity(self.nodes[0].p_op*self.nodes[1].p_op))
        print(self.fidelity)
        # fidelity decrease by memorying during sending pauli frame
        self.fidelity = Fidelity.decohere_by_time(self.fidelity, p_to_fidelity(self.nodes[0].p_mem), self.distance)
        print(self.fidelity)
        print(self.distance)
        print(self.nodes[0].p_mem)
        print(p_to_fidelity(self.nodes[0].p_mem))
        self.fidelity = Fidelity.decohere_by_time(self.fidelity, p_to_fidelity(self.nodes[1].p_mem), self.distance)
        print(self.fidelity)
            
        #print(self.fidelity, self.blocking_times)
        return True
    def calc_new_fidelity_by_purification(self) -> float:
        return Fidelity.calc_new_fidelity_by_purification(self.fidelity, self.fidelity)
    def calc_new_blocking_time_by_purification(self):
        # have to be called before fidelity gets updated
        success_rate = Fidelity.calc_success_rate_of_purification(self.fidelity, self.fidelity)
        new_bt_int_node_ = self.blocking_times.blocking_time_int_node * 2
        new_bt_end_node_ = self.blocking_times.blocking_time_end_node * 2
        for node in self.nodes:
            if node.is_end_node:
                new_bt_end_node_ += self.distance
            else:
                new_bt_int_node_ += self.distance
        new_bt_int_node = new_bt_int_node_ / success_rate
        new_bt_end_node = new_bt_end_node_ / success_rate
        return BlockingTimes(new_bt_int_node, new_bt_end_node)
    def calc_success_rate_of_purification(self) -> float:
        return Fidelity.calc_success_rate_of_purification(self.fidelity, self.fidelity)

    def repeat_purification_until_target_fidelity(self, target_fidelity):
        while self.fidelity.fidelity < target_fidelity:
            if not self.process_purification():
                return False
        return True

class LocalBellPairProcessor(BellPairProcessor):
    def __init__(self, node_left: Node, node_right: Node, link: Link) -> None:
        self.node_left = node_left
        self.node_right = node_right
        
        super().__init__(None, None)

        self.link = link
        self.fidelity = Fidelity(link.fidelity_raw_bellpair)

        if node_left.is_end_node and node_right.is_end_node:
            self.blocking_times = BlockingTimes(0, 2)
        elif node_left.is_end_node or node_right.is_end_node:
            self.blocking_times = BlockingTimes(1, 1)
        else:
            self.blocking_times = BlockingTimes(2, 0)

    def register_nodes(self):
        return [self.node_left, self.node_right], None

    def calc_distance(self) -> int:
        return 1

