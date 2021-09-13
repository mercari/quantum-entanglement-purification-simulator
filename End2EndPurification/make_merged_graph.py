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
import functools as ft

def main():
    """
    parameter_file_name = sys.argv[1]
    parameter_module_name = parameter_file_name.split("/")[1].split(".")[0]
    parameter_module = import_module(parameter_module_name)
    """

    directory_root = '../data_generalizd_fidelity1/'
    fidelity_raw_bellpair_ = 0.8
    layer2_target_fidelity = [0.9, 0.99, 0.999]
    layer3_target_fidelity = [0.9, 0.99, 0.999]
    layer4_target_fidelity = [0.99] #, 0.99, 0.9]
    p_op_int_node_  = 0.00001
    p_mem_int_node_ = 0.00001
    p_op_end_node_  = 0.00001
    p_mem_end_node_ = 0.00001

    # [i for i in range(100, 2001, 100)]

    #print(len(num_nodes))
    #print(len(false_e2e_final_int_node))
    #print(false_e2e_final_total_node)


    #colors = ['b', 'g', 'r', 'c', 'm', 'y', 'pink', 'xkcd:bright green']
    cycle = plt.rcParams['axes.prop_cycle'].by_key()['color'] # ココがポイント

    #markersize, fontsize = 4, 6
    markersize, fontsize = 3, 15
    plt.rcParams["font.size"] = fontsize
    plt.tight_layout()

    start = 3
    for stop in [64, 256]:
        num_nodes = [i for i in range(start, stop+1)]
        #plt.gca().set_xlim(right=stop)


        for bt_type in ["int", "end", "total"]:
            c = 0

            fig, ax = plt.subplots(figsize=(10,10),dpi=200) 
            ax.set_yscale('log')
            ax.set_xlim(start, stop)
            ax.set_ylim(0.01, 10**7)
            ax.grid(color='g', which='major', linestyle=':', linewidth=0.5)
            ax.minorticks_on()
            ax.grid(color='g', which='minor', linestyle=':', linewidth=0.1)
            def add(a,b):
                return a+b
            ax.set_yticks(ft.reduce(add, [[10**j * i for i in range(1, 10)] for j in range (-2, 7)]), minor=True)

            done = []
            for layer2_target_fidelity_ in layer2_target_fidelity:
                for layer3_target_fidelity_ in layer3_target_fidelity:
                    #if layer3_target_fidelity_ > layer2_target_fidelity_:
                    #    continue
                    for layer4_target_fidelity_ in layer4_target_fidelity:
                        #if layer4_target_fidelity_ > layer3_target_fidelity_ or layer4_target_fidelity_ > layer2_target_fidelity_:
                        #   continue
                        #color = colors[c]
                        color = cycle[c]
                        c += 1

                        comb = (layer2_target_fidelity_, None, layer4_target_fidelity_) 
                        if comb not in done:
                            purification_at_int_nodes_ = False
                            false_e2e_final_int_node, false_e2e_final_end_node, false_e2e_final_total_node = collect_num_node(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_nodes, purification_at_int_nodes_)
                            label = "l2:%.3f, l3:None,  l4:%.3f"%(layer2_target_fidelity_,  layer4_target_fidelity_)
                            if bt_type == "int":
                                ax.plot(num_nodes, false_e2e_final_int_node, label=label, ls='solid', marker='+', color=color, markersize=markersize, lw=1)
                            elif bt_type == "end":
                                ax.plot(num_nodes, false_e2e_final_end_node, label=label, ls='solid', marker='+', color=color, markersize=markersize, lw=1)
                            elif bt_type == "total":
                                ax.plot(num_nodes, false_e2e_final_total_node, label=label, ls='solid', marker='+', color=color, markersize=markersize, lw=1)
                            done.append(comb)
                        else:
                            pass

                        purification_at_int_nodes_ = True
                        true_e2e_final_int_node, true_e2e_final_end_node, true_e2e_final_total_node = collect_num_node(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_nodes, purification_at_int_nodes_)
                        label = "l2:%.3f, l3:%.3f, l4:%.3f"%(layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_)
                        if layer2_target_fidelity_ == 0.9 and layer3_target_fidelity_ == 0.99 and layer4_target_fidelity_ == 0.9:
                            print(true_e2e_final_int_node)
                        if bt_type == "int":
                            ax.plot(num_nodes, true_e2e_final_int_node, label=label, ls='dotted', marker='x', color=color, markersize=markersize, lw=1)
                        elif bt_type == "end":
                            ax.plot(num_nodes, true_e2e_final_end_node, label=label, ls='dotted', marker='x', color=color, markersize=markersize, lw=1)
                        elif bt_type == "total":
                            ax.plot(num_nodes, true_e2e_final_total_node, label=label, ls='dotted', marker='x', color=color, markersize=markersize, lw=1)
            ax.set_xlabel('The number of nodes (Linear Network)', fontsize=fontsize)
            ax.set_ylabel('Occupying quantum memory time', fontsize=fontsize)
            if bt_type == "int":
                title = "Intermediate Node\n"
            elif bt_type == "end":
                title = "End Node\n"
            elif bt_type == "total":
                title = "Total\n"
            title += "p_op_int_node:%.1e, p_mem_int_node:%.1e, \np_op_end_node:%.1e, p_mem_end_node:%.1e, \n#nodes:%d-%d"%(p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, start, stop)
            ax.set_title(title, fontsize=fontsize)
            ax.legend(fontsize=fontsize, ncol=2)
            #plt.show()
            fig.savefig(directory_root + title.replace("\n","") + ".pdf", bbox_inches='tight', pad_inches=0)


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
    def multi_order(a):
        unit_time = 1
        if isinstance(a, float):
            return a * unit_time
        else:
            return None
    return list(map(multi_order, e2e_final_int_node)), list(map(multi_order, e2e_final_end_node)), list(map(multi_order, e2e_final_total_node))
 
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

