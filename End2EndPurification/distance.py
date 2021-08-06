class Distance:
    speed:int = 200000
    c:int = 299792.458
        # 200,000 # km/s in optical fiber
        # 299,792.458 # km/s in free space
    def __init__(self, distance, transmission_time) -> None:
        self.distance = distance
        self.transmission_time = transmission_time
    def calc_duration(self):
        return self.distance / self.speed
    def calc_time_unit(self, time_unit_length):
        return self.calc_duration() / time_unit_length
    @staticmethod
    def sum_distances(distance_left, distance_right):
        return Distance(distance_left.distance + distance_right.distance, distance_left.transmission_time + distance_right.transmission_time)
