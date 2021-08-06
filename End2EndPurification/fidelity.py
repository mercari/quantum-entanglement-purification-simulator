class Fidelity:
    def __init__(self, fidelity) -> None:
        self.fidelity = fidelity
    def __repr__(self) -> str:
        return str(self.fidelity)
    @staticmethod
    def decohere_by_time(input_fidelity,  memory_fidelity, num):
        # used for memory error
        return Fidelity(input_fidelity.fidelity * (memory_fidelity**num))
    @staticmethod
    def calc_new_fidelity_by_entanglement_swapping(input_fidelity_left, input_fidelity_right, node_left, node_middle, node_right):
        # including:
        # - fidelities of source bell pairs
        # - operation error of E.S. in the middle node
        # - memory error in the left and right nodes
        return Fidelity(input_fidelity_left.fidelity * input_fidelity_right.fidelity * p_to_fidelity(node_left.p_mem) * p_to_fidelity(node_middle.p_op) * p_to_fidelity(node_right.p_mem))
    @staticmethod
    def calc_new_fidelity_by_purification(input_fidelity_left, input_fidelity_right, node_left, node_right):
        # including:
        # - fidelities of source bell pairs
        # - improvement by purification itself
        # - operation error of E.S.
        return Fidelity(input_fidelity_left.fidelity * input_fidelity_right.fidelity / (input_fidelity_left.fidelity * input_fidelity_right.fidelity + (1-input_fidelity_left.fidelity)*(1-input_fidelity_right.fidelity)) * p_to_fidelity(node_left.p_op) * p_to_fidelity(node_right.p_op))
    @staticmethod
    def calc_success_rate_of_purification(input_fidelity_left, input_fidelity_right):
        return input_fidelity_left.fidelity * input_fidelity_right.fidelity + (1-input_fidelity_left.fidelity) * (1-input_fidelity_right.fidelity)

def p_to_fidelity(p):
    return 1-p

def fidelity_to_p(fidelity):
    return 1-fidelity
