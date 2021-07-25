import sys, os, time
import json
import itertools, functools
import concurrent.futures
from importlib import import_module
import shutil

def main():
    parameter_file_name = sys.argv[1]
    parameter_module_name = parameter_file_name.split("/")[1].split(".")[0]
    parameter_module = import_module(parameter_module_name)

    directory_root, fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes = parameter_module.parameters()

    if not os.path.exists(directory_root):
        os.makedirs(directory_root, exist_ok=True)
    shutil.copy(parameter_file_name, directory_root)


    length = calc_parameter_product_length(parameter_module.parameters)
    time.sleep(1)

    cases = itertools.product([(length, directory_root)], fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes)

    with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
        executor.map(one_process, zip(range(length), cases))

def calc_parameter_product_length(parameters):
    def times(a,b):
        return a*b
    length = functools.reduce(times, map(len, parameters()))
    return length
    
def one_process(num_case):
    num, case = num_case
    (length, directory_root), fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_ = case

    directory, file_output, file_input = generate_file_name(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_)
    json_dict = {
        'fidelity_raw_bellpair': fidelity_raw_bellpair_,
        'layer2_target_fidelity': layer2_target_fidelity_,
        'layer3_target_fidelity': layer3_target_fidelity_,
        'layer4_target_fidelity': layer4_target_fidelity_,
        'p_op_int_node': p_op_int_node_,
        'p_mem_int_node': p_mem_int_node_,
        'p_op_end_node': p_op_end_node_,
        'p_mem_end_node': p_mem_end_node_,
        'num_node': num_node_,
        'purification_at_int_nodes': purification_at_int_nodes_,
        'file_out': file_output
    }

    print("{:,}/{:,}".format(num,length))
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(file_input, 'w') as fd:
        json.dump(json_dict, fd, indent=4)

def generate_file_name(directory_root, fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_):
    base_string = \
    str(fidelity_raw_bellpair_) + "_" +\
    str(layer2_target_fidelity_) + "_" +\
    str(layer3_target_fidelity_) + "_" +\
    str(layer4_target_fidelity_) + "_" +\
    str(p_op_int_node_) + "_" +\
    str(p_mem_int_node_) + "_" +\
    str(p_op_end_node_) + "_" +\
    str(p_mem_end_node_) + "_" +\
    str(num_node_) + "_" +\
    str(purification_at_int_nodes_)

    directory = \
    directory_root + "/" +\
    str(fidelity_raw_bellpair_) + "/" +\
    str(layer2_target_fidelity_) + "/" +\
    str(layer3_target_fidelity_) + "/" +\
    str(layer4_target_fidelity_) + "/" +\
    str(p_op_int_node_) + "/" +\
    str(p_mem_int_node_) + "/" +\
    str(p_op_end_node_) + "/" +\
    str(p_mem_end_node_) + "/" +\
    str(num_node_) + "/" +\
    str(purification_at_int_nodes_)

    file_input = directory + "/" + base_string + "_input.json"
    file_output = directory + "/" + base_string + "_output.json"
    #print (directory, file_output, file_input)
    return directory, file_output, file_input


if __name__ == '__main__':
    main()
