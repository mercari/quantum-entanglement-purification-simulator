def parameters():
    directory_root = '../data1/'
    fidelity_raw_bellpair = [0.8]
    layer2_target_fidelity = [0.9, 0.99, 0.999, 0.9999]
    layer3_target_fidelity = [0.9, 0.99, 0.999, 0.9999]
    layer4_target_fidelity = [0.9, 0.99, 0.999, 0.9999]
    p_op_int_node = [0.01, 0.001, 0.0001]
    p_mem_int_node = [0.01, 0.001, 0.0001]
    p_op_end_node = [0.01, 0.001, 0.0001]
    p_mem_end_node = [0.01, 0.001, 0.0001]
    num_node = [i for i in range(2, 65)] # [i for i in range(100, 2001, 100)]
    purification_at_int_nodes = [False, True]
    
    return directory_root, fidelity_raw_bellpair,layer2_target_fidelity,layer3_target_fidelity,layer4_target_fidelity,p_op_int_node,p_mem_int_node,p_op_end_node,p_mem_end_node,num_node,purification_at_int_nodes
    