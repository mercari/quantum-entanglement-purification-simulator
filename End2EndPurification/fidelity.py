from typing import Tuple, List
import numpy as np
from scipy.linalg import fractional_matrix_power
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
        # - memory error in the left and right nodes during operation
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


class FidelityGeneralizedModel(Fidelity):
    def __init__(self, fidelity) -> None:
        self.input = fidelity
        # Equ. 9.17
        if isinstance(fidelity, float):
            self.state = np.array([fidelity, (1-fidelity)/3, (1-fidelity)/3, (1-fidelity)/3])
        elif isinstance(fidelity, np.ndarray):
            self.state = fidelity
        elif isinstance(fidelity, Tuple) or isinstance(fidelity, List) and len(fidelity) == 4:
            a,b,c,d = fidelity
            self.state = np.array([a, b, c, d])
        else:
            print("class Fidelity input error.")
            assert(False)
    def __repr__(self) -> str:
        return str(self.state)
    @property
    def fidelity(self):
        return self.state[0]
    @property
    def a(self):
        return self.state[0]        
    @property
    def b(self):
        return self.state[1]
    @property
    def c(self):
        return self.state[2]
    @property
    def d(self):
        return self.state[3]
    @staticmethod
    def decohere_by_time(input_fidelity,  memory_fidelity, num):
        # used for memory error
        noisy_i = np.array([
            [memory_fidelity, (1-memory_fidelity)/3, (1-memory_fidelity)/3, (1-memory_fidelity)/3],
            [(1-memory_fidelity)/3, memory_fidelity, (1-memory_fidelity)/3, (1-memory_fidelity)/3],
            [(1-memory_fidelity)/3, (1-memory_fidelity)/3, memory_fidelity, (1-memory_fidelity)/3],
            [(1-memory_fidelity)/3, (1-memory_fidelity)/3, (1-memory_fidelity)/3, memory_fidelity]
        ])
        u = np.linalg.matrix_power(noisy_i, int(num))
        new_state = np.dot(u, input_fidelity.state)
        return FidelityGeneralizedModel(new_state)
    @staticmethod
    def calc_new_fidelity_by_entanglement_swapping(input_fidelity_left, input_fidelity_right, node_left, node_middle, node_right):
        # including:
        # - fidelities of source bell pairs
        # - operation error of E.S. in the middle node
        # - memory error in the left and right nodes during operation
        #
        # φ+・φ+ → φ+ aa → a
        # φ+・ψ+ → ψ+ ab → b
        # φ+・ψ- → ψ- ac → c
        # φ+・φ- → φ- ad
        #
        # ψ+・φ+ → ψ+ ba → b
        # ψ+・ψ+ → φ+ bb → a
        # ψ+・ψ- → φ- bc
        # ψ+・φ- → ψ- bd → c
        #
        # ψ-・φ+ → ψ- ca → c
        # ψ-・ψ+ → φ- cb
        # ψ-・ψ- → φ+ cc → a
        # ψ-・φ- → ψ+ cd → b
        #
        # φ-・φ+ → φ- da
        # φ-・ψ+ → ψ- db → c
        # φ-・ψ- → ψ+ dc → b
        # φ-・φ- → φ+ dd → a

        # - fidelities of source bell pairs
        #print("states:", input_fidelity_left.state, input_fidelity_right.state)
        fid = FidelityGeneralizedModel.calc_new_fidelity_by_entanglement_swapping_alg(input_fidelity_left, input_fidelity_right)
        #print("infunc, fid:1", fid.state)
        # - operation error of E.S. in the middle node
        #print("node_middle.unit_time/node_middle.unit_time:", node_middle.unit_time/node_middle.unit_time)
        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(node_middle.p_op), node_middle.unit_time/node_middle.unit_time)
        # - memory error in the left and right nodes during operation
        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(node_left.p_mem), node_left.unit_time/node_middle.unit_time)
        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(node_right.p_mem), node_right.unit_time/node_middle.unit_time)
        #print("infunc, fid:2", fid.state)

        return fid
    @staticmethod
    def calc_new_fidelity_by_entanglement_swapping_alg(input_fidelity_left, input_fidelity_right):
        # - fidelities of source bell pairs
        #print("states:", input_fidelity_left.state, input_fidelity_right.state)
        a = np.dot(input_fidelity_left.state, input_fidelity_right.state)
        b = np.dot(input_fidelity_left.state, np.dot(np.array([[0,1,0,0],[1,0,0,0],[0,0,0,1],[0,0,1,0]]), input_fidelity_right.state))
        c = np.dot(input_fidelity_left.state, np.dot(np.array([[0,0,1,0],[0,0,0,1],[1,0,0,0],[0,1,0,0]]), input_fidelity_right.state))
        d = np.dot(input_fidelity_left.state, np.dot(np.array([[0,0,0,1],[0,0,1,0],[0,1,0,0],[1,0,0,0]]), input_fidelity_right.state))
        fid = FidelityGeneralizedModel((a,b,c,d)) 
        return fid      
    @staticmethod
    def calc_new_fidelity_by_purification(input_fidelity_left, input_fidelity_right, node_left, node_right):
        # including:
        # - fidelities of source bell pairs
        # - improvement by purification itself
        # - operation error of E.S.
        # ** finally, Hadamard **
       
        # - fidelities of source bell pairs
        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(input_fidelity_left, input_fidelity_right)
        fid = FidelityGeneralizedModel(abcd / FidelityGeneralizedModel.calc_success_rate_of_purification(input_fidelity_left, input_fidelity_right))
        #print("fid in FidelityG",fid)

        # - operation error of E.S.
        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(node_left.p_mem), node_left.unit_time/max(node_left.unit_time, node_right.unit_time))
        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(node_right.p_mem), node_right.unit_time/max(node_left.unit_time, node_right.unit_time))

        # ** finally, Hadamard **
        # error transition
        # I→I
        # X→Z
        # Y→Y
        # Z→X
        fid = FidelityGeneralizedModel(np.dot(np.array([[1,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,0,0]]), fid.state))

        return fid

    @staticmethod
    def calc_new_fidelity_by_purification_alg(input_fidelity_left, input_fidelity_right):

        # φ+・φ+ → φ+ even aa → a
        # φ+・ψ+ → φ+ odd  ab → discard
        # φ+・ψ- → φ- odd  ac → discard
        # φ+・φ- → φ- even ad → d
        #
        # ψ+・φ+ → ψ+ odd  ba → discard
        # ψ+・ψ+ → ψ+ even bb → b
        # ψ+・ψ- → ψ- even bc → c
        # ψ+・φ- → ψ- odd  bd → discard
        #
        # ψ-・φ+ → ψ- odd  ca → discard
        # ψ-・ψ+ → ψ- even cb → c
        # ψ-・ψ- → ψ+ even cc → b
        # ψ-・φ- → ψ+ odd  cd → discard
        #
        # φ-・φ+ → φ- even da → d
        # φ-・ψ+ → ψ- odd  db → discard
        # φ-・ψ- → ψ+ odd  dc → discard
        # φ-・φ- → φ+ even dd → a

        # - fidelities of source bell pairs
        # - improvement by purification itself
        #print("input_fidelity_left", input_fidelity_left)
        a = np.dot(input_fidelity_left.state, np.dot(np.array([[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,1]]), input_fidelity_right.state))
        b = np.dot(input_fidelity_left.state, np.dot(np.array([[0,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,0]]), input_fidelity_right.state))
        c = np.dot(input_fidelity_left.state, np.dot(np.array([[0,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,0]]), input_fidelity_right.state))
        d = np.dot(input_fidelity_left.state, np.dot(np.array([[0,0,0,1],[0,0,0,0],[0,0,0,0],[1,0,0,0]]), input_fidelity_right.state))
        #print("abcd",a,b,c,d)
 
        return (a,b,c,d)
    @staticmethod
    def calc_success_rate_of_purification(input_fidelity_left, input_fidelity_right):
        la, lb, lc, ld = input_fidelity_left.state
        ra, rb, rc, rd = input_fidelity_right.state
        return ((la+ld)*(ra+rd)+(lb+lc)*(rb+rc))

