#from _typeshed import Self
import sys
import json
import math
from typing import Dict, Tuple
try:
    from fidelity import Fidelity, fidelity_to_p, p_to_fidelity
except:
    from End2EndPurification.fidelity import Fidelity, fidelity_to_p, p_to_fidelity

try:
    from distance import Distance
except:
    from End2EndPurification.distance import Distance

try: 
    from bellpair_processor import BellPairProcessor, LocalBellPairProcessor, Node, Link
except:
    from End2EndPurification.bellpair_processor import BellPairProcessor, LocalBellPairProcessor, Node, Link

try:
    from blocking_times import BlockingTimes
except:
    from End2EndPurification.blocking_times import BlockingTimes

class Config:
    def __init__(self, arg) -> None:
        if isinstance(arg, Dict):
            json_dict = arg
            self.fidelity_raw_bellpair = float(json_dict['fidelity_raw_bellpair'])
            self.layer2_target_fidelity = float(json_dict['layer2_target_fidelity'])
            self.layer3_target_fidelity = float(json_dict['layer3_target_fidelity'])
            self.layer4_target_fidelity = float(json_dict['layer4_target_fidelity'])
            self.p_op_int_node = float(json_dict['p_op_int_node'])
            self.p_mem_int_node = float(json_dict['p_mem_int_node'])
            self.p_op_end_node = float(json_dict['p_op_end_node'])
            self.p_mem_end_node = float(json_dict['p_mem_end_node'])
            self.num_node = int(json_dict['num_node'])
            self.purification_at_int_nodes = bool(json_dict['purification_at_int_nodes'])
            self.file_out = json_dict['file_out']
            self.settings = json_dict
        elif isinstance(arg, Tuple):
            fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes, file_out = arg
            self.fidelity_raw_bellpair = fidelity_raw_bellpair
            self.layer2_target_fidelity = layer2_target_fidelity
            self.layer3_target_fidelity = layer3_target_fidelity
            self.layer4_target_fidelity = layer4_target_fidelity
            self.p_op_int_node = p_op_int_node
            self.p_mem_int_node = p_mem_int_node
            self.p_op_end_node = p_op_end_node
            self.p_mem_end_node = p_mem_end_node
            self.num_node = num_node
            self.purification_at_int_nodes = purification_at_int_nodes
            self.file_out = file_out
        else:
            print("config load error")
            return False

def load_json(json_file):
    with open(json_file, 'r') as fd:
        json_dict = json.load(fd)
        config = Config(json_dict)

    return config

def save_json(json_file, link_fidelity, link_bt_int_node, link_bt_end_node, e2e_raw_fidelity, e2e_raw_bt_int_node, e2e_raw_bt_end_node, e2e_final_fidelity, e2e_final_bt_int_node, e2e_final_bt_end_node, settings):
    json_dict = {
                    'success': True,
                    'link': {
                        'fidelity': link_fidelity.fidelity,
                        'bt_int_node': link_bt_int_node,
                        'bt_end_node': link_bt_end_node
                    },
                    'e2e_raw':{
                        'fidelity': e2e_raw_fidelity.fidelity,
                        'bt_int_node': e2e_raw_bt_int_node,
                        'bt_end_node': e2e_raw_bt_end_node
                    },
                    'e2e_final':{
                        'fidelity': e2e_final_fidelity.fidelity,
                        'bt_int_node': e2e_final_bt_int_node,
                        'bt_end_node': e2e_final_bt_end_node
                    },
                    'settings': settings
                }
    with open(json_file, 'w') as fd:
        json.dump(json_dict, fd, indent=4)

def main():
    if sys.argv.__len__() == 2:
        run_with_setting_file(sys.argv[1])
        return True
    elif sys.argv.__len__() == 11:
        fidelity_raw_bellpair = float(sys.argv[1])
        layer2_target_fidelity = float(sys.argv[2])
        layer3_target_fidelity = float(sys.argv[3])
        layer4_target_fidelity = float(sys.argv[4])
        p_op_int_node = float(sys.argv[5])
        p_mem_int_node = float(sys.argv[6])
        p_op_end_node = float(sys.argv[7])
        p_mem_end_node = float(sys.argv[8])
        num_node = int(sys.argv[9]) # linear network
        purification_at_int_nodes = bool(sys.argv[10])
        file_out = None
        config = Config((fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes, file_out))

        run(config)
        return True
    print("Error. Simulation don't run.")
    return False

def run_with_setting_file(setting_file):
    config = load_json(setting_file)

    run(config)

def run(config):
    nodes, links = prepare_nodes_and_links(config)

    output = calc_fidelity_and_blocking_time(nodes, links, config)
    if output is False:
        with open(config.file_out, 'w') as fd:
            json.dump({'success': False,'settings': config.setting}, fd, indent=4)
        return
    #print(output)
    (link_fidelity, bt_link), (e2e_raw_fidelity, bt_e2e_raw), (e2e_final_fidelity, bt_e2e_final) = output
    link_bt_int_node, link_bt_end_node = bt_link.blocking_time_int_node, bt_link.blocking_time_end_node
    e2e_raw_bt_int_node, e2e_raw_bt_end_node = bt_e2e_raw.blocking_time_int_node, bt_e2e_raw.blocking_time_end_node
    e2e_final_bt_int_node, e2e_final_bt_end_node = bt_e2e_final.blocking_time_int_node, bt_e2e_final.blocking_time_end_node
    if config.file_out:
        save_json(config.file_out, link_fidelity, link_bt_int_node, link_bt_end_node, e2e_raw_fidelity, e2e_raw_bt_int_node, e2e_raw_bt_end_node, e2e_final_fidelity, e2e_final_bt_int_node, e2e_final_bt_end_node, config.settings)

def prepare_nodes_and_links(config):
    nodes = [Node(True, config.p_op_end_node, config.p_mem_end_node)] + [Node(False, config.p_op_int_node, config.p_mem_int_node) for _ in range(config.num_node-2)] + [Node(True, config.p_op_end_node, config.p_mem_end_node)]
    links = []
    for i in range(config.num_node-1):
        link = Link(config.fidelity_raw_bellpair)
        links.append(link)
        nodes[i].connect_to(nodes[i+1], link)
        link.connect(nodes[i], nodes[i+1])
    return nodes, links

def calc_fidelity_and_blocking_time(nodes, links, config):
    bpp_single_layer = []
    bpp_all_layers = [bpp_single_layer]

    # generate Layer2 bpp 
    for i in range(len(links)):
        local_bpp = LocalBellPairProcessor(nodes[i], nodes[i+1], links[i])
        bpp_single_layer.append(local_bpp)
    
    # process Layer2 bpp (each link bpp)
    if not process_layer2_bpp(bpp_all_layers, config.layer2_target_fidelity):
        return False
    example_l2 = bpp_all_layers[0][0].fidelity, bpp_all_layers[0][0].blocking_times

    # process Layer3 bpp
    if not process_layer3_bpp(bpp_all_layers, config.purification_at_int_nodes, config.layer3_target_fidelity):
        return False
    example_l3 = bpp_all_layers[-1][0].fidelity, bpp_all_layers[-1][0].blocking_times

    # process Layer4 bpp (End-to-End bpp)
    if not process_layer4_bpp(bpp_all_layers, config.layer4_target_fidelity):
        return False
    result = bpp_all_layers[-1][0].fidelity, bpp_all_layers[-1][0].blocking_times

    return example_l2, example_l3, result

def process_layer4_bpp(bpp_all_layers, layer4_target_fidelity):
    bpp = bpp_all_layers[-1][-1]
    if not bpp.repeat_purification_until_target_fidelity(layer4_target_fidelity):
        return False
    return True

def process_layer2_bpp(bpp_all_layers, layer2_target_fidelity):
    bpp_single_layer = bpp_all_layers[0]
    for local_bpp in bpp_single_layer:
        if not local_bpp.repeat_purification_until_target_fidelity(layer2_target_fidelity):
            return False
    return True

def process_layer3_bpp(bpp_all_layers, purification_at_int_nodes, layer3_target_fidelity):
    bpp_single_layer = bpp_all_layers[-1]
    while True:
        res, bpp_single_layer = process_layer3_bpp_one_round(bpp_single_layer, purification_at_int_nodes, layer3_target_fidelity)

        if res:
            bpp_all_layers.append(bpp_single_layer)
        else:
            return False

        if bpp_single_layer.__len__() == 1:
            # End-to-End bpp is achieved
            break
    return True

def process_layer3_bpp_one_round(bpp_single_layer_prev, purification_at_int_nodes, layer3_target_fidelity):
    bpp_single_layer = []

    tmp = bpp_single_layer_prev.copy()
    while tmp != []:
        if tmp.__len__() == 1:
            bpp_single_layer.append(tmp.pop(0))
            break
        bpp = BellPairProcessor(tmp.pop(0), tmp.pop(0))
        bpp.process_entanglement_swapping()
        bpp_single_layer.append(bpp)
        if purification_at_int_nodes:
            if not bpp.repeat_purification_until_target_fidelity(layer3_target_fidelity):
                return False, None
    return True, bpp_single_layer


if __name__ == "__main__":
    main()

