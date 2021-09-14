import math

try:
    from fidelity import FidelityGeneralizedModel as Fidelity
    from fidelity import fidelity_to_p, p_to_fidelity
except:
    from End2EndPurification.fidelity import FidelityGeneralizedModel as Fidelity
    from End2EndPurification.fidelity import fidelity_to_p, p_to_fidelity

try:
    from blocking_times import BlockingTimes
except:
    from End2EndPurification.blocking_times import BlockingTimes

try:
    from distance import Distance
except:
    from End2EndPurification.distance import Distance

class Link:
    def __init__(self, fidelity_raw_bellpair, distance=20, speed=200000) -> None:
        self.fidelity_raw_bellpair = fidelity_raw_bellpair
        self.nodes = []
        self.distance = Distance(distance, distance / speed)
    def connect(self, node_left, node_right):
        self.nodes.append(node_left)
        self.nodes.append(node_right)

class Node:
    id = 0
    def __init__(self, is_end_node: bool, p_op: float, p_mem: float, unit_time: float = 0.0001) -> None:
        self.neighbor = []
        self.links = []
        self.is_end_node = is_end_node
        self.p_op = p_op 
        self.p_mem = p_mem 
        self.unit_time = unit_time # sec # operation time # unit to calculate memory error
        self.id = Node.id
        Node.id += 1
    def __repr__(self):
        return "<id:" + repr(self.id) + ", num_neighbor:" + repr(len(self.neighbor)) + ",is_end_node:" + repr(self.is_end_node) + ">"
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
    def copy(self):
        bpp = BellPairProcessor(self.bpp_left, self.bpp_right)
        bpp.fidelity = self.fidelity
        bpp.blocking_times = self.blocking_times
        return bpp
    def register_nodes(self):
        nodes = []
        for node in self.bpp_left.nodes + self.bpp_right.nodes:
            if node in nodes:
                nodes.remove(node)
                mid_node = node
            else:
                nodes.append(node)
        assert(nodes.__len__() == 2)
        return nodes, mid_node
 
    def calc_distance(self) -> int:
        return Distance.sum_distances(self.bpp_left.distance, self.bpp_right.distance)
    def process_entanglement_swapping(self):
        # 1 BPP毎に1回しか呼び出されない

        # Respectively,
        # fidelity decrease by E.S. itself 
        # fidelity decrease by operation (gate) error
        # (fidelity decrease by memorying) <- next operation does not need to wait pauli frames of E.S.
        self.fidelity = self.calc_new_fidelity_by_entanglement_swapping()
        #print(__name__, self.fidelity)
        #(((1-self.nodes[0].p_mem) * (1-self.nodes[1].p_mem))**(self.distance)) * \

        self.blocking_times = self.calc_new_blocking_time_by_entanglement_swapping()
    def calc_new_fidelity_by_entanglement_swapping(self):
        return Fidelity.calc_new_fidelity_by_entanglement_swapping(self.bpp_left.fidelity, self.bpp_right.fidelity, self.nodes[0], self.mid_node, self.nodes[1])
    def calc_new_blocking_time_by_entanglement_swapping(self) -> int:
        bt = BlockingTimes.merge_blocking_times(self.bpp_left.blocking_times, self.bpp_right.blocking_times)
        return bt

    def process_purification(self):
        #print("self.fidelity.fidelity", self.fidelity.fidelity)
        if self.fidelity.fidelity <= 0.5 or self.blocking_times.blocking_time_int_node >= BlockingTimes.LIMIT or self.blocking_times.blocking_time_end_node >= BlockingTimes.LIMIT:
            # fidelity less than 0.5 cannot be improved
            return False
        
        success_rate = self.calc_success_rate_of_purification()
        
        # log for debug
        self.success_rate_repetition_log.append(success_rate)
        self.fidelity_repetition_log.append(self.fidelity)
        self.blocking_time_repetition_log.append(self.blocking_times)

        self.blocking_times = self.calc_new_blocking_time_by_purification()

        #print(self.fidelity)

        # fidelity increase by purification  
        # fidelity decrease by operation (gate) error
        self.fidelity = self.calc_new_fidelity_by_purification()

        #print(self.fidelity)

        # fidelity decrease by memorying during sending pauli frame
        self.fidelity = self.calc_decoherence_during_classical_transmission()

        #print(self.fidelity, self.blocking_times)

        return True
    def calc_new_fidelity_by_purification(self) -> float:
        return Fidelity.calc_new_fidelity_by_purification(self.fidelity, self.fidelity, self.nodes[0], self.nodes[1])
    def calc_decoherence_during_classical_transmission(self):
        fid = Fidelity.decohere_by_time(self.fidelity, p_to_fidelity(self.nodes[0].p_mem), self.distance.transmission_time / self.nodes[0].unit_time)
        fid = Fidelity.decohere_by_time(fid, p_to_fidelity(self.nodes[1].p_mem), self.distance.transmission_time / self.nodes[1].unit_time)
        return fid
    def calc_new_blocking_time_by_purification(self):
        # have to be called before fidelity gets updated
        success_rate = Fidelity.calc_success_rate_of_purification(self.fidelity, self.fidelity)
        new_bt = BlockingTimes.merge_blocking_times(self.blocking_times, self.blocking_times)
        for node in self.nodes:
            if node.is_end_node:
                # operation
                ## for the 1st Bell pair
                new_bt = BlockingTimes.add_blocking_times(new_bt, 0, node.unit_time)
                ## for the 2nd Bell pair
                new_bt = BlockingTimes.add_blocking_times(new_bt, 0, node.unit_time)
                # waiting for pauli frame vie classical connection for the remaining (1st) Bell pair
                new_bt = BlockingTimes.add_blocking_times(new_bt, 0, self.distance.transmission_time)
            else:
                # operation
                ## for the 1st Bell pair
                new_bt = BlockingTimes.add_blocking_times(new_bt, node.unit_time, 0)
                ## for the 2nd Bell pair
                new_bt = BlockingTimes.add_blocking_times(new_bt, node.unit_time, 0)
                # waiting for pauli frame vie classical connection
                new_bt = BlockingTimes.add_blocking_times(new_bt, self.distance.transmission_time , 0)
        new_bt = BlockingTimes.multiply_blocking_times(new_bt, 1/success_rate)
        return new_bt
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
        self.link = link
       
        super().__init__(None, None)

        self.fidelity = Fidelity(link.fidelity_raw_bellpair)

        bt_int_node = 0
        bt_end_node = 0
        for node in {node_left, node_right}:
            if node.is_end_node:
                # init Bell pair
                bt_end_node += node.unit_time
            else:
                # init Bell pair
                bt_int_node += node.unit_time
        self.blocking_times = BlockingTimes(bt_int_node, bt_end_node)
        #print("lbpp init:", self.blocking_times)

    def register_nodes(self):
        return [self.node_left, self.node_right], None

    def calc_distance(self) -> int:
        return self.link.distance

    def copy(self):
        bpp = LocalBellPairProcessor(self.node_left, self.node_right, self.link)
        bpp.fidelity = self.fidelity
        bpp.blocking_times = self.blocking_times
        return bpp