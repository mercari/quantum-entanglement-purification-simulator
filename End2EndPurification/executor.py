import sys, os, time, datetime
import json
import itertools, functools
from math import floor
import concurrent.futures
from generate_simulation_cases import generate_file_name, calc_parameter_product_length
from e2ep import run_with_setting_file, run
from config import Config
from importlib import import_module
import shutil

def main():
    parameter_file_name = sys.argv[1]
    parameter_module_name = parameter_file_name.split("/")[1].split(".")[0]
    parameter_module = import_module(parameter_module_name)

    param = parameter_module.Parameters()

    if not os.path.exists(param.directory_root):
        os.makedirs(param.directory_root, exist_ok=True)
    shutil.copy(parameter_file_name, param.directory_root)

    length = calc_parameter_product_length(param.iterating_parameters())

    num_workers = 9
    start_and_stop = [(floor(length*i/num_workers), floor(length*(i+1)/num_workers)) for i in range(num_workers)]
    print(start_and_stop)
    time.sleep(1)

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        for i in range(num_workers):
            executor.submit(one_process, param, i, start_and_stop)

def one_process(param, i, start_and_stop):
    length = calc_parameter_product_length(param.iterating_parameters())

    cases = itertools.product([(length, param.directory_root)], param.fidelity_raw_bellpair, param.layer2_target_fidelity, param.layer3_target_fidelity, param.layer4_target_fidelity, param.p_op_int_node, param.p_mem_int_node, param.p_op_end_node, param.p_mem_end_node, param.num_node, param.purification_at_int_nodes)

    print(start_and_stop[i][0], start_and_stop[i][1])
    gen = itertools.islice(cases, start_and_stop[i][0], start_and_stop[i][1])

    print("one_process")
    length = start_and_stop[i][1] - start_and_stop[i][0]
    print("length:%d"%length)
    count = 0
    start_time = datetime.datetime.now()
    for case in gen:
        count += 1
        one_simulation(case)
        if i == 0:
            print("{:,}/{:,}".format(count,length), datetime.datetime.now() - start_time, case)


def one_simulation(case):
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

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    config = Config(json_dict)

    retval = run(config)

    return retval




if __name__ == '__main__':
    main()
