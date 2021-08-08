import sys, os, time, datetime
import json
import itertools, functools
from math import floor
import concurrent.futures
from generate_simulation_cases import generate_file_name, calc_parameter_product_length
from e2ep import run_with_setting_file, run
from importlib import import_module
import numpy as np
import matplotlib.pyplot as plt

def main():
    """
    parameter_file_name = sys.argv[1]
    parameter_module_name = parameter_file_name.split("/")[1].split(".")[0]
    parameter_module = import_module(parameter_module_name)
    """

    directory_root = "../data1/"
    fidelity_raw_bellpair_ = 0.8
    layer2_target_fidelity_ = 0.99
    layer3_target_fidelity_ = 0.9
    layer4_target_fidelity_ = 0.99
    p_op_int_node_  = 0.001
    p_mem_int_node_ = 0.001
    p_op_end_node_  = 0
    p_mem_end_node_ = 0

    # [i for i in range(100, 2001, 100)]

    purification_at_int_nodes_ = False

    num_nodes = [i for i in range(2, 65)]

    false_e2e_final_int_node, false_e2e_final_end_node, false_e2e_final_total_node = collect_num_node(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_nodes, purification_at_int_nodes_)

    purification_at_int_nodes_ = True

    true_e2e_final_int_node, true_e2e_final_end_node, true_e2e_final_total_node = collect_num_node(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_nodes, purification_at_int_nodes_)

    print(len(num_nodes))
    print(len(false_e2e_final_int_node))
    print(false_e2e_final_total_node)

    fig, ax = plt.subplots(figsize=(10,10),dpi=200) 
    ax.set_yscale('log')
    ax.plot(num_nodes, false_e2e_final_int_node, label='Block. Time of Int. Node with only E2E Pur.', ls='solid', marker='o', color='blue')
    ax.plot(num_nodes, false_e2e_final_end_node, label='Block. Time of End Node with only E2E Pur.', ls='solid', marker='v', color='blue')
    ax.plot(num_nodes, false_e2e_final_total_node, label='Block. Time of Both Nodes with only E2E Pur.', ls='solid', marker='s', color='blue')
    ax.plot(num_nodes, true_e2e_final_int_node, label='Block. Time of Int. Node with non-E2E Pur.', ls='dashed', marker='o', color='red')
    ax.plot(num_nodes, true_e2e_final_end_node, label='Block. Time of End Node with non-E2E Pur.', ls='dashed', marker='v', color='red')
    ax.plot(num_nodes, true_e2e_final_total_node, label='Block. Time of Both Nodes with non-E2E Pur.', ls='dashed', marker='s', color='red')
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel('Consuming Blocking Time')
    title = "l2:%f, l3:%f, l4:%f, \np_op_int_node:%.1e, p_mem_int_node:%.1e, p_op_end_node:%.1e, p_mem_end_node:%.1e"%(layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_)
    ax.set_title(title)
    ax.legend()
    plt.show()
    fig.savefig(directory_root + title + ".pdf")


def collect_num_node(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_nodes, purification_at_int_nodes_):
    e2e_final_int_node = []
    e2e_final_end_node = []
    e2e_final_total_node = []    
    for num_node_ in num_nodes:
        directory, file_output, file_input = generate_file_name(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_)
        with open(file_output, 'r') as fd:
            json_dict = json.load(fd)
            if json_dict["success"]:
                e2e_final_int_node.append(json_dict["e2e_final"]["bt_int_node"])
                e2e_final_end_node.append(json_dict["e2e_final"]["bt_end_node"])
                e2e_final_total_node.append(json_dict["e2e_final"]["bt_int_node"] + json_dict["e2e_final"]["bt_end_node"])
            else:
                e2e_final_int_node.append(None)
                e2e_final_end_node.append(None)
                e2e_final_total_node.append(None)
    return e2e_final_int_node, e2e_final_end_node, e2e_final_total_node
 
def collect_results(cases, data):
    # For purification_at_int_nodes,
    # 0 for False
    # 1 for True
    for case in cases:
        (length, directory_root), fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_ = case

        directory, file_output, file_input = generate_file_name(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_)

        if purification_at_int_nodes_:
            purification_at_int_nodes__ = 1
        else:
            purification_at_int_nodes__ = 0

        data[fidelity_raw_bellpair_][layer2_target_fidelity_][layer3_target_fidelity_][layer4_target_fidelity_][p_op_int_node_][p_mem_int_node_][p_op_end_node_][p_mem_end_node_][num_node_][purification_at_int_nodes__] = file_output
    

if __name__ == "__main__":
    main()

