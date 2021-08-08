import json
from typing import Dict, Tuple

class Config:
    def __init__(self, arg) -> None:
        # Default
        self.fidelity_raw_bellpair = 0.99
        self.layer2_target_fidelity = 0.99
        self.layer3_target_fidelity = 0.99
        self.layer4_target_fidelity = 0.99
        self.p_op_int_node = 0.001
        self.p_mem_int_node = 0.001
        self.p_op_end_node = 0.001
        self.p_mem_end_node = 0.001
        self.num_node = 5
        self.purification_at_int_nodes = True
        self.file_out = None

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
            print("Default configuration is set.")

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