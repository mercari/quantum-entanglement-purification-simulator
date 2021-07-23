import sys
import json

def parameters():
    directory_in = 'input/'
    directory_out = 'output/'
    fidelity_raw_bellpair = [0.84]
    local_target_fidelity = [0.99, 0.999, 0.9999]
    target_fidelity = [0.99, 0.999, 0.9999]
    p_op_int_node = [0.01, 0.001, 0.0001]
    p_mem_int_node = [0.01, 0.001, 0.0001]
    p_op_end_node = [0.01, 0.001, 0.0001]
    p_mem_end_node = [0.01, 0.001, 0.0001]
    num_node = [i for i in range(2, 66)]
    purification_at_int_nodes = [False, True]
    return directory_in, directory_out, fidelity_raw_bellpair,local_target_fidelity,target_fidelity,p_op_int_node,p_mem_int_node,p_op_end_node,p_mem_end_node,num_node,purification_at_int_nodes

def main():
    directory_in, directory_out, fidelity_raw_bellpair, local_target_fidelity, target_fidelity, p_op_int_node, p_mem_int_node, p_op_end_node, p_mem_end_node, num_node, purification_at_int_nodes = parameters()

    for fidelity_raw_bellpair_ in fidelity_raw_bellpair:
        for local_target_fidelity_ in local_target_fidelity:
            for target_fidelity_ in target_fidelity:
                for p_op_int_node_ in p_op_int_node:
                    for p_mem_int_node_ in p_mem_int_node:
                        for p_op_end_node_ in p_op_end_node:
                            for p_mem_end_node_ in p_mem_end_node:
                                for num_node_ in num_node:
                                    for purification_at_int_nodes_ in purification_at_int_nodes:
                                        base_string = \
                                        str(fidelity_raw_bellpair_) + "_" +\
                                        str(local_target_fidelity_) + "_" +\
                                        str(target_fidelity_) + "_" +\
                                        str(p_op_int_node_) + "_" +\
                                        str(p_mem_int_node_) + "_" +\
                                        str(p_op_end_node_) + "_" +\
                                        str(p_mem_end_node_) + "_" +\
                                        str(num_node_) + "_" +\
                                        str(purification_at_int_nodes_)
                                        file_input = directory_in + base_string + "_input.json"
                                        file_output = directory_out + base_string + "_output.json"
                                        json_dict = {
                                            'fidelity_raw_bellpair': fidelity_raw_bellpair_,
                                            'local_target_fidelity': local_target_fidelity_,
                                            'target_fidelity': target_fidelity_,
                                            'p_op_int_node': p_op_int_node_,
                                            'p_mem_int_node': p_mem_int_node_,
                                            'p_op_end_node': p_op_end_node_,
                                            'p_mem_end_node': p_mem_end_node_,
                                            'num_node': num_node_,
                                            'purification_at_int_nodes': purification_at_int_nodes_,
                                            'file_out': file_output
                                        }
                                        with open(file_input, 'w') as fd:
                                            json.dump(json_dict, fd, indent=4)


if __name__ == '__main__':
    main()
