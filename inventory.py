from builtins import dict, zip, map, int, len

import numpy

"""
orders = [
    {
        "restaurant_ID": "R1",
        "order_time": "2020-12-08 21:15:31",
        "order_ID": "ORDER1",
        "foods": ["BLT", "LT", "VLT"]
    }
]
"""
branch_capacity_keys = [
    "burger_cook_cap",
    "burger_cook_time",
    "burger_ass_cap",
    "burger_ass_time",
    "burger_pack_cap",
    "burger_pack_time",
    "inventory_burger_cap",
    "inventory_lettuce_cap",
    "inventory_tomato_cap",
    "inventory_veggie_cap",
    "inventory_bacon_cap",
]

inventory_material_mapping = {
    "L": "inventory_lettuce_cap",
    "T": "inventory_tomato_cap",
    "B": "inventory_bacon_cap",
}


class Inventory:
    def __init__(self, branch_capacity, limit_time=20):
        self.branch_capacity_raw_values = branch_capacity
        self.total_process_time = 0
        self.preprocess_branch_inventory_capacity()
        self.ready_burger_time = self.branch_capacity["burger_cook_time"] + \
                                 self.branch_capacity["burger_ass_time"] + \
                                 self.branch_capacity["burger_pack_time"]
        self.limit_time = limit_time
        self.calculate_max_burger_number_based_on_limit_time()

    def process_order(self, order):
        burger_cook_cap ,burger_ass_cap, burger_pack_cap=self.store_current_state_of_burger_capacity()
        order_process_time = 0
        foods = self.extract_foods_list_from_order(order)
        if len(foods) > self.max_burger:
            return self.log_rejected_order(order)
        for food in foods:
            if not self.is_burger_inventory_has_capacity(food[0]): #first character of food is burger_type
                return self.log_rejected_order(order)
            for material in food[1:]:
                if not self.is_material_inventory_has_capacity(material):
                    return self.log_rejected_order(order)
                # start the process
            food_process_time = self.calculate_process_time()
            order_process_time += food_process_time
            self.increase_burger_capacity_waiting_time()
        if order_process_time > 20:
            self.restore_prev_state_of_burger_capacity(
                (burger_cook_cap ,burger_ass_cap, burger_pack_cap))
            return self.log_rejected_order(order)

        self.add_order_process_time_to_total_time(order_process_time)
        return self.log_accepted_order(order, order_process_time)

    def preprocess_branch_inventory_capacity(self):
        self.branch_capacity_values = [int(var) if var.isdigit() else int(var[:-1]) for var in
                                  self.branch_capacity_raw_values.split(",")[1:]]
        self.branch_capacity = dict(zip(branch_capacity_keys, self.branch_capacity_values))
        self.burger_cook_cap = numpy.zeros(self.branch_capacity["burger_cook_cap"])
        self.burger_ass_cap = numpy.zeros(self.branch_capacity["burger_ass_cap"])
        self.burger_pack_cap = numpy.zeros(self.branch_capacity["burger_pack_cap"])

    @staticmethod
    def extract_foods_list_from_order(order):
        order = order.split(",")
        return order[3:]

    def get_inventories_state(self):
        return f'{self.branch_capacity["inventory_burger_cap"]},' \
               f'{self.branch_capacity["inventory_lettuce_cap"]},{self.branch_capacity["inventory_tomato_cap"]},' \
               f'{self.branch_capacity["inventory_veggie_cap"]},{self.branch_capacity["inventory_bacon_cap"]}'

    def get_total_process_time(self):
        return self.total_process_time

    def is_burger_inventory_has_capacity(self, burger_type):
        if burger_type == "V":  # veggie burger
            if self.branch_capacity["inventory_veggie_cap"] == 0:
                return False
            self.branch_capacity["inventory_veggie_cap"] -= 1
        else:  # burger
            if self.branch_capacity["inventory_burger_cap"] == 0:
                return False
            self.branch_capacity["inventory_burger_cap"] -= 1
        return True

    def is_material_inventory_has_capacity(self, material):
        if self.branch_capacity[inventory_material_mapping[material]] == 0:
            return False
        self.branch_capacity[inventory_material_mapping[material]] -= 1
        return True

    def calculate_process_time(self):
        process_time = self.ready_burger_time
        process_time += self.burger_cook_cap[0] + self.burger_ass_cap[0] + self.burger_pack_cap[0]
        return process_time

    @staticmethod
    def log_rejected_order(order):
        order = order.split(",")
        return f'{order[0]},{order[2]},REJECTED'

    @staticmethod
    def log_accepted_order(order, process_time):
        order = order.split(",")
        return f'{order[0]},{order[2]},ACCEPTED,{process_time}'

    def add_order_process_time_to_total_time(self, process_time):
        self.total_process_time += process_time

    def increase_burger_capacity_waiting_time(self):
        self.burger_cook_cap[0] += self.branch_capacity["burger_cook_time"]
        self.burger_cook_cap.sort()
        self.burger_ass_cap[0] += self.branch_capacity["burger_ass_time"]
        self.burger_ass_cap.sort()
        self.burger_pack_cap[0] += self.branch_capacity["burger_pack_time"]
        self.burger_pack_cap.sort()

    def store_current_state_of_burger_capacity(self):
        return self.burger_cook_cap[0] , self.burger_ass_cap[0], self.burger_pack_cap[0]

    def restore_prev_state_of_burger_capacity(self, tuple):
        self.burger_cook_cap[0] = tuple[0]
        self.burger_cook_cap.sort()
        self.burger_ass_cap[0] = tuple[1]
        self.burger_ass_cap.sort()
        self.burger_pack_cap[0] = tuple[2]
        self.burger_pack_cap.sort()

    def calculate_max_burger_number_based_on_limit_time(self):
        self.max_burger = self.limit_time/self.ready_burger_time
