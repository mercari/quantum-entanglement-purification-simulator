#from _typeshed import Self
import sys
import json

def load_json(json_file):
    with open(json_file, 'r') as fd:
        json_dict = json.load(fd)

        fidelity_raw_bellpair = float(json_dict['fidelity_raw_bellpair'])
        local_target_fidelity = float(json_dict['local_target_fidelity'])
        target_fidelity = float(json_dict['target_fidelity'])
        p_op_int_node = float(json_dict['p_op_int_node'])
        p_mem_int_node = float(json_dict['p_mem_intnode'])
        p_op_end_node = float(json_dict['p_op_end_node'])
        p_mem_end_node = float(json_dict['p_mem_end_node'])
        num_node = int(json_dict['num_node'])
        purification_at_int_nodes = bool(json_dict['purification_at_int_nodes'])
        file_out = json_dict['file_out']

    return fidelity_raw_bellpair, local_target_fidelity, target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes, file_out, json_dict

def save_json(json_file, link_fidelity, link_bt_int_node, link_bt_end_node, e2e_raw_fidelity, e2e_raw_bt_int_node, e2e_raw_bt_end_node, e2e_final_fidelity, e2e_final_bt_int_node, e2e_final_bt_end_node, settings):
    json_dict = {
                    'success': True,
                    'link': {
                        'fidelity': link_fidelity,
                        'bt_int_node': link_bt_int_node,
                        'bt_end_node': link_bt_end_node
                    },
                    'e2e_raw':{
                        'fidelity': e2e_raw_fidelity,
                        'bt_int_node': e2e_raw_bt_int_node,
                        'bt_end_node': e2e_raw_bt_end_node
                    },
                    'e2e_final':{
                        'fidelity': e2e_final_fidelity,
                        'bt_int_node': e2e_final_bt_int_node,
                        'bt_end_node': e2e_final_bt_end_node
                    },
                    'settings': settings
                }
    with open(json_file, 'w') as fd:
        json.dump(json_dict, fd, indent=4)

def main():
    if sys.argv.__len__() == 2:
        fidelity_raw_bellpair, local_target_fidelity, target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes, file_out, settings = load_json(sys.argv[1])
    else:
        fidelity_raw_bellpair = float(sys.argv[1])
        local_target_fidelity = float(sys.argv[2])
        target_fidelity = float(sys.argv[3])
        p_op_int_node = float(sys.argv[4])
        p_mem_int_node = float(sys.argv[5])
        p_op_end_node = float(sys.argv[6])
        p_mem_end_node = float(sys.argv[7])
        num_node = int(sys.argv[8]) # linear network
        purification_at_int_nodes = bool(sys.argv[9])
        file_out = None
        settings = None
    
    nodes, links = prepare_nodes_and_links(num_node, fidelity_raw_bellpair, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node)

    output = calc_fidelity_and_blocking_time(nodes, links, local_target_fidelity, target_fidelity, purification_at_int_nodes)
    if output is False:
        with open(file_out, 'w') as fd:
            json.dump({'success': False,'settings': settings}, fd, indent=4)
        return
    print(output)
    (link_fidelity, bt_link), (e2e_raw_fidelity, bt_e2e_raw), e2e_final_fidelity, bt_e2e_final = output
    link_bt_int_node, link_bt_end_node = bt_link.blocking_time_int_node, bt_link.blocking_time_end_node
    e2e_raw_bt_int_node, e2e_raw_bt_end_node = bt_e2e_raw.blocking_time_int_node, bt_e2e_raw.blocking_time_end_node
    e2e_final_bt_int_node, e2e_final_bt_end_node = bt_e2e_final.blocking_time_int_node, bt_e2e_final.blocking_time_end_node
    if file_out:
        save_json(file_out, link_fidelity, link_bt_int_node, link_bt_end_node, e2e_raw_fidelity, e2e_raw_bt_int_node, e2e_raw_bt_end_node, e2e_final_fidelity, e2e_final_bt_int_node, e2e_final_bt_end_node, settings)

def prepare_nodes_and_links(num_node, fidelity_raw_bellpair, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node):
    nodes = [Node(True, p_op_end_node, p_mem_end_node)] + [Node(False, p_op_int_node, p_mem_int_node) for _ in range(num_node-2)] + [Node(True, p_op_end_node, p_mem_end_node)]
    links = []
    for i in range(num_node-1):
        link = Link(fidelity_raw_bellpair)
        links.append(link)
        nodes[i].connect_to(nodes[i+1], link)
        link.connect(nodes[i], nodes[i+1])
    return nodes, links

def calc_fidelity_and_blocking_time(nodes, links, local_target_fidelity, target_fidelity, purification_at_int_nodes):
    bpp_single_layer = []
    bpp_all_layers = [bpp_single_layer]
    for i in range(len(links)):
        local_bpp = LocalBellPairProcessor(nodes[i], nodes[i+1], links[i])
        bpp_single_layer.append(local_bpp)
    
    for local_bpp in bpp_single_layer:
        if not local_bpp.repeat_purification_until_target_fidelity(local_target_fidelity):
            return False
        tmp1 = local_bpp.fidelity, local_bpp.blocking_times

    while True:
        bpp_single_layer_prev = bpp_single_layer
        bpp_single_layer = []
        bpp_all_layers.append(bpp_single_layer)

        tmp = bpp_single_layer_prev.copy()
        while tmp != []:
            if tmp.__len__() == 1:
                bpp_single_layer.append(tmp.pop(0))
                break
            bpp = BellPairProcessor(tmp.pop(0), tmp.pop(0))
            bpp.process_entanglement_swapping()
            bpp_single_layer.append(bpp)
            if purification_at_int_nodes:
                if not bpp.repeat_purification_until_target_fidelity(target_fidelity):
                    return False
        if bpp_single_layer.__len__() == 1:
            break
    bpp = bpp_all_layers[-1][-1]
    tmp2 = bpp.fidelity, bpp.blocking_times
    if not bpp.repeat_purification_until_target_fidelity(target_fidelity):
        return False
    return tmp1, tmp2, bpp.fidelity, bpp.blocking_times


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
        
        self.nodes = self.register_nodes()

       # log for debug
        self.fidelity_repetition_log = []
        self.blocking_time_repetition_log = []
        self.success_rate_repetition_log = []
    def register_nodes(self):
        nodes = []
        for node in self.bpp_left.nodes + self.bpp_right.nodes:
            if node in nodes:
                nodes.remove(node)
            else:
                nodes.append(node)
        assert(nodes.__len__() == 2)
        return nodes
 
    def calc_distance(self) -> int:
        return self.bpp_left.distance + self.bpp_right.distance
    def process_entanglement_swapping(self):
        # 1 BPP毎に1回しか呼び出されない

        # Respectively,
        # fidelity decrease by E.S. itself 
        # fidelity decrease by operation (gate) error
        # (fidelity decrease by memorying) <- next operation does not need to wait pauli frames of E.S.
        self.fidelity = calc_new_fidelity_by_entanglement_swapping(self.bpp_left.fidelity, self.bpp_right.fidelity) * \
            (1-self.nodes[0].p_op) * (1-self.nodes[1].p_op)
            #(((1-self.nodes[0].p_mem) * (1-self.nodes[1].p_mem))**(self.distance)) * \

        self.blocking_times = self.calc_new_blocking_time_by_entanglement_swapping()
    def calc_new_blocking_time_by_entanglement_swapping(self) -> int:
        btl = BlockingTimes(self.bpp_left.blocking_times.blocking_time_int_node + self.bpp_right.blocking_times.blocking_time_int_node,
                                self.bpp_left.blocking_times.blocking_time_end_node + self.bpp_right.blocking_times.blocking_time_end_node)
        return btl

    def process_purification(self):
        if self.fidelity <= 0.5 or self.blocking_times.blocking_time_int_node >= BlockingTimes.LIMIT or self.blocking_times.blocking_time_end_node >= BlockingTimes.LIMIT:
            # fidelity less than 0.5 cannot be improved
            return False
        success_rate = calc_success_rate_of_purification(self.fidelity, self.fidelity)
        
        self.success_rate_repetition_log.append(success_rate)
        self.fidelity_repetition_log.append(self.fidelity)
        self.blocking_time_repetition_log.append(self.blocking_times)

        self.blocking_times = self.calc_new_blocking_time_by_purification()

        # Respectively,
        # fidelity increase by purification  
        # fidelity decrease by operation (gate) error
        # fidelity decrease by memorying during sending pauli frame
        self.fidelity = calc_new_fidelity_by_purification(self.fidelity, self.fidelity) * \
           (((1-self.nodes[0].p_mem) * (1-self.nodes[1].p_mem))**(self.distance)) * \
           (1-self.nodes[0].p_op) * (1-self.nodes[1].p_op)
            
        print(self.fidelity, self.blocking_times)
        return True
    def calc_new_fidelity_by_purification(self) -> float:
        return calc_new_fidelity_by_purification(self.fidelity, self.fidelity)
    def calc_new_blocking_time_by_purification(self):
        # have to be called before fidelity gets updated
        success_rate = calc_success_rate_of_purification(self.fidelity, self.fidelity)
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
        return calc_success_rate_of_purification(self.fidelity, self.fidelity)

    def repeat_purification_until_target_fidelity(self, target_fidelity):
        while self.fidelity < target_fidelity:
            if not self.process_purification():
                return False
        return True

class LocalBellPairProcessor(BellPairProcessor):
    def __init__(self, node_left: Node, node_right: Node, link: Link) -> None:
        self.node_left = node_left
        self.node_right = node_right
        
        super().__init__(None, None)

        self.link = link
        self.fidelity = link.fidelity_raw_bellpair

        if node_left.is_end_node and node_right.is_end_node:
            self.blocking_times = BlockingTimes(0, 2)
        elif node_left.is_end_node or node_right.is_end_node:
            self.blocking_times = BlockingTimes(1, 1)
        else:
            self.blocking_times = BlockingTimes(2, 0)

    def register_nodes(self):
        return [self.node_left, self.node_right]

    def calc_distance(self) -> int:
        return 1

class BlockingTimes:
    LIMIT = 1000000
    def __init__(self, bloking_time_int_node, blocking_time_end_node) -> None:
        self.blocking_time_int_node = bloking_time_int_node
        self.blocking_time_end_node = blocking_time_end_node
    def __repr__(self):
        return "(b_time_interm_node:"+ '{:.5g}'.format(self.blocking_time_int_node) +", b_time_end_node:"+ '{:.5g}'.format(self.blocking_time_end_node) + ")"

def calc_new_fidelity_by_entanglement_swapping(input_fidelity_left, input_fidelity_right) -> float:
    return input_fidelity_left * input_fidelity_right

def calc_new_fidelity_by_purification(input_fidelity_left, input_fidelity_right) -> float:
    return input_fidelity_left * input_fidelity_right / (input_fidelity_left * input_fidelity_right + (1-input_fidelity_left)*(1-input_fidelity_right))

def calc_success_rate_of_purification(input_fidelity_left, input_fidelity_right):
    return input_fidelity_left * input_fidelity_right + (1-input_fidelity_left) * (1-input_fidelity_right)


if __name__ == "__main__":
    main()

