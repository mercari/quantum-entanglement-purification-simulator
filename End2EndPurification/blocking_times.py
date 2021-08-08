class BlockingTimes:
    LIMIT = 1000000
    def __init__(self, bloking_time_int_node, blocking_time_end_node) -> None:
        self.blocking_time_int_node = bloking_time_int_node
        self.blocking_time_end_node = blocking_time_end_node
    def __repr__(self):
        return "(b_time_interm_node:"+ '{:.5g}'.format(self.blocking_time_int_node) +", b_time_end_node:"+ '{:.5g}'.format(self.blocking_time_end_node) + ")"
    @staticmethod
    def merge_blocking_times(bt_left, bt_right):
        return BlockingTimes(bt_left.blocking_time_int_node+bt_right.blocking_time_int_node, bt_left.blocking_time_end_node + bt_right.blocking_time_end_node)
    @staticmethod
    def add_blocking_times(self, blocking_time_int_node, blocking_time_end_node):
        return BlockingTimes(self.blocking_time_int_node + blocking_time_int_node, self.blocking_time_end_node + blocking_time_end_node)
    @staticmethod
    def multiply_blocking_times(self, multiplier):
        return BlockingTimes(self.blocking_time_int_node * multiplier, self.blocking_time_end_node * multiplier)
