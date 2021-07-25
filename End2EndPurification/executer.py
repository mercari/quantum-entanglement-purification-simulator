import sys, os, time, datetime
import json
import itertools, functools
from math import floor
import concurrent.futures
from parameters import parameters
from generate_simulation_cases import generate_file_name, calc_parameter_product_length
from e2ep import run_with_setting_file, run

def main():
    directory_root, fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes = parameters()

    length = calc_parameter_product_length(parameters)

    cases = itertools.product([(length, directory_root)], fidelity_raw_bellpair, layer2_target_fidelity, layer3_target_fidelity, layer4_target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes)

    num_workers = 9
    start_and_stop = [(floor(length*i/num_workers), floor(length*(i+1)/num_workers)) for i in range(num_workers)]
    print(start_and_stop)
    time.sleep(1)

    with concurrent.futures.ProcessPoolExecutor(max_workers=num_workers) as executor:
        for i in range(num_workers):
            executor.submit(one_process, cases, i, start_and_stop)

def one_process(cases, i, start_and_stop):
    print("one_process")
    gen = itertools.islice(cases, start_and_stop[i][0], start_and_stop[i][1])
    length = start_and_stop[i][1] - start_and_stop[i][0]
    print("length:%d"%length)
    count = 0
    start_time = datetime.datetime.now()
    for case in gen:
        count += 1
        one_simulation(case)
        if i == 0:
            print("{:,}/{:,}".format(count,length), datetime.datetime.now() - start_time)


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

    retval = run(fidelity_raw_bellpair_, layer2_target_fidelity_, layer3_target_fidelity_, layer4_target_fidelity_, p_op_int_node_, p_mem_int_node_, p_op_end_node_, p_mem_end_node_, num_node_, purification_at_int_nodes_, file_output, 
    json_dict)

    return retval




if __name__ == '__main__':
    main()
