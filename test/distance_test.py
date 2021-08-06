from unittest import TestCase
from End2EndPurification.distance import Distance

class DistanceTest(TestCase):
    def setUp(self) -> None:
        self.distance = Distance(1, 1/200000)
        return super().setUp()
    def test_calc_duration(self):
        self.assertEqual(self.distance.calc_duration(), 1/200000)
    def test_calc_time_unit(self):
        self.assertEqual(self.distance.calc_time_unit(0.001), 1/200000/0.001)
    def test_sum_distances(self):
        distance_left = Distance(20000, 20000/200000)
        distance_right = Distance(40000, 40000/200000)
        sd = Distance.sum_distances(distance_left, distance_right)
        self.assertEqual(sd.distance, 60000)
        self.assertAlmostEqual(sd.transmission_time, 60000 / 200000)
