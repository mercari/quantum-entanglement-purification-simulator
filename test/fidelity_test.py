from unittest import TestCase
from End2EndPurification.fidelity import Fidelity, FidelityGeneralizedModel, p_to_fidelity, fidelity_to_p
from End2EndPurification.bellpair_processor import Node
import numpy as np
import itertools
class FidelityTest(TestCase):
    def setUp(self) -> None:
        self.fidelity = Fidelity(0.99)
        self.node_left = Node(True, 0.01, 0.02) # p_op, p_mem
        self.node_middle = Node(None, 0.0001, 0.0002, 0.00001)
        self.node_right = Node(False, 0.001, 0.002)
        return super().setUp()
    def test_decohere_by_time(self):
        self.assertAlmostEqual(Fidelity.decohere_by_time(self.fidelity, self.node_left.p_mem, 2).fidelity, 0.99*0.02*0.02)
    def test_calc_new_fidelity_by_entanglement_swapping(self):
        fidelity_left = Fidelity(0.98)
        fidelity_right = Fidelity(0.97)
        self.assertEqual(Fidelity.calc_new_fidelity_by_entanglement_swapping(fidelity_left, fidelity_right, self.node_left, self.node_middle, self.node_right).fidelity, 0.98*0.97*(1-0.02)*(1-0.0001)*(1-0.002))
    def test_calc_new_fidelity_by_purification(self):
        fidelity_left = Fidelity(0.99)
        fidelity_right = Fidelity(0.97)
        self.assertEqual(Fidelity.calc_new_fidelity_by_purification(fidelity_left, fidelity_right, self.node_left, self.node_right).fidelity, 0.99*0.97 / (0.99 * 0.97 + 0.01 * 0.03)*(1-0.01) * (1-0.001))
    def test_calc_success_rate_of_purification(self):
        fidelity_left = Fidelity(0.99)
        fidelity_right = Fidelity(0.97)
        self.assertEqual(Fidelity.calc_success_rate_of_purification(fidelity_left, fidelity_right), 0.99*0.97+0.01*0.03)

class FidelityGeneralizedModelTest(TestCase):
    def setUp(self) -> None:
        self.fidelity = FidelityGeneralizedModel(0.99)
        self.node_left = Node(True, 0.01, 0.02) # p_op, p_mem
        self.node_middle = Node(None, 0.0001, 0.0002, 0.0001)
        self.node_right = Node(False, 0.001, 0.002)
        return super().setUp()
    def test_decohere_by_time(self):
        fid = FidelityGeneralizedModel.decohere_by_time(self.fidelity, p_to_fidelity(self.node_left.p_mem), 1)
        val = np.array([0.99*0.98+0.01/3*0.02/3*3,
        0.99*0.02/3+0.01/3*0.98+0.01/3*0.02/3+0.01/3*0.02/3,
        0.99*0.02/3+0.01/3*0.98+0.01/3*0.02/3+0.01/3*0.02/3,
        0.99*0.02/3+0.01/3*0.98+0.01/3*0.02/3+0.01/3*0.02/3
        ])
        for i in range(len(val)):
            self.assertAlmostEqual(float(fid.state[i]), val[i])

        fid = FidelityGeneralizedModel.decohere_by_time(fid, p_to_fidelity(self.node_left.p_mem), 1)

        val = [val[0]*0.98 + val[1]*0.02/3 + val[2]*0.02/3 + val[3]*0.02/3,
        val[0]*0.02/3 + val[1]*0.98 + val[2]*0.02/3 + val[3]*0.02/3,
        val[0]*0.02/3 + val[1]*0.02/3 + val[2]*0.98 + val[3]*0.02/3,
        val[0]*0.02/3 + val[1]*0.02/3 + val[2]*0.02/3 + val[3]*0.98]

        for i in range(len(val)):
            self.assertAlmostEqual(float(fid.state[i]), val[i])

    def test_calc_new_fidelity_by_entanglement_swapping(self):
        fidelity_left = FidelityGeneralizedModel(0.98)
        fidelity_right = FidelityGeneralizedModel(0.97)
        fid = FidelityGeneralizedModel.calc_new_fidelity_by_entanglement_swapping(fidelity_left, fidelity_right, self.node_left, self.node_middle, self.node_right)
        
        la, lb, lc, ld = fidelity_left.a, fidelity_left.b, fidelity_left.c, fidelity_left.d
        ra, rb, rc, rd = fidelity_right.a, fidelity_right.b, fidelity_right.c, fidelity_right.d
        val = (la*ra+lb*rb+lc*rc+ld*rd, la*rb+lb*ra+lc*rd+rc*ld, la*rc+ra*lc+lb*rd+rb*ld, la*rd+ra*ld+lb*rc+lc*rb)
        val = FidelityGeneralizedModel.decohere_by_time(FidelityGeneralizedModel(val), p_to_fidelity(self.node_middle.p_op), self.node_middle.unit_time/self.node_middle.unit_time)
        val = FidelityGeneralizedModel.decohere_by_time(val, p_to_fidelity(self.node_left.p_mem), self.node_left.unit_time/self.node_middle.unit_time)
        val = FidelityGeneralizedModel.decohere_by_time(val, p_to_fidelity(self.node_right.p_mem), self.node_right.unit_time/self.node_middle.unit_time)

        print("fid",fid.state)
        print("val:",val)
        for i in range(len(val.state)):
            self.assertAlmostEqual(float(fid.state[i]), float(val.state[i]))

    def test_calc_new_fidelity_by_entanglement_swapping_alg(self):
        fidelity_left = FidelityGeneralizedModel(0.98)
        fidelity_right = FidelityGeneralizedModel(0.97)
        fid = FidelityGeneralizedModel.calc_new_fidelity_by_entanglement_swapping_alg(fidelity_left, fidelity_right)
        
        la, lb, lc, ld = fidelity_left.a, fidelity_left.b, fidelity_left.c, fidelity_left.d
        ra, rb, rc, rd = fidelity_right.a, fidelity_right.b, fidelity_right.c, fidelity_right.d
        val = (la*ra+lb*rb+lc*rc+ld*rd, la*rb+lb*ra+lc*rd+rc*ld, la*rc+ra*lc+lb*rd+rb*ld, la*rd+ra*ld+lb*rc+lc*rb)

        print("fid",fid.state)
        print("val:",val)
        for i in range(len(val)):
            self.assertAlmostEqual(float(fid.state[i]), val[i])

        self.assertAlmostEqual(sum(fid.state), 1)

    def test_calc_new_fidelity_by_purification(self):
        fidelity_left = FidelityGeneralizedModel(0.98)
        fidelity_right = FidelityGeneralizedModel(0.97)
        fid = FidelityGeneralizedModel.calc_new_fidelity_by_purification(fidelity_left, fidelity_right, self.node_left, self.node_right)
        print("fid",fid)
        self.assertAlmostEqual(sum(fid.state), 1)

    def test_calc_new_fidelity_by_purification_alg(self):
        # φ+ ψ+ ψ- φ-
        for i, vec1 in zip(range(4), [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]):
            fidelity_left = FidelityGeneralizedModel(vec1)
            for j, vec2 in zip(range(4), [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]):
                fidelity_right = FidelityGeneralizedModel(vec2)
                if i==0:
                    if j==0:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [1,0,0,0])
                    elif j==1:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==2:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==3:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,1])
                elif i==1:
                    if j==0:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==1:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,1,0,0])
                    elif j==2:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,1,0])
                    elif j==3:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                elif i==2:
                    # φ+ ψ+ ψ- φ-
                    if j==0:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==1:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,1,0])
                    elif j==2:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,1,0,0])
                    elif j==3:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                elif i==3:
                    if j==0:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,1])
                    elif j==1:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==2:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [0,0,0,0])
                    elif j==3:
                        abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fidelity_left, fidelity_right)
                        self.assertListEqual(list(abcd), [1,0,0,0])

                #abcd = FidelityGeneralizedModel.calc_new_fidelity_by_purification_alg(fid, fid)

    def test_calc_success_rate_of_purification(self):
        fidelity_left = FidelityGeneralizedModel(0.99)
        fidelity_right = FidelityGeneralizedModel(0.97)
        self.assertEqual(FidelityGeneralizedModel.calc_success_rate_of_purification(fidelity_left, fidelity_right), (0.99+0.01/3)*(0.97+0.03/3)+(0.01*2/3)*(0.03*2/3))


