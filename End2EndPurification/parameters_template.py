class Parameters:
    def __init__(self) -> None:
        self.directory_root = '../data1/'
        self.fidelity_raw_bellpair = [0.8]
        self.layer2_target_fidelity = [0.9, 0.95, 0.99, 0.999, 0.9999]
        self.layer3_target_fidelity = [0.9, 0.95, 0.99, 0.999, 0.9999]
        self.layer4_target_fidelity = [0.9, 0.95, 0.99, 0.999, 0.9999]
        self.p_op_int_node = [0.01, 0.001, 0.0001]
        self.p_mem_int_node = [0.01, 0.001, 0.0001]
        self.p_op_end_node = [0.01, 0.001, 0.0001, 0]
        self.p_mem_end_node = [0.01, 0.001, 0.0001, 0]
        self.num_node = [i for i in range(2, 65)] # [i for i in range(100, 2001, 100)]
        self.purification_at_int_nodes = [False, True]
    def iterating_parameters(self):
        return self.fidelity_raw_bellpair,self.layer2_target_fidelity,self.layer3_target_fidelity,self.layer4_target_fidelity,self.p_op_int_node,self.p_mem_int_node,self.p_op_end_node,self.p_mem_end_node,self.num_node,self.purification_at_int_nodes
    