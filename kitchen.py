from builtins import dict, zip, map, int, len
from datetime import datetime, timedelta

import numpy


kitchen_capacity_keys = [
    "burger_cook_cap",
    "burger_cook_time",
    "burger_ass_cap",
    "burger_ass_time",
    "burger_pack_cap",
    "burger_pack_time",
    "inventory_burger",
    "inventory_lettuce",
    "inventory_tomato",
    "inventory_veggie",
    "inventory_bacon",
]

inventory_material_mapping = {
    "L": "inventory_lettuce",
    "T": "inventory_tomato",
    "B": "inventory_bacon",
}


class Kitchen:
    def __init__(self, capacity, limit_time=20):
        self.capacity = capacity
        self.total_process_time = 0
        self.preprocess_capacity()
        self.burger_process_time = self.capacity["burger_cook_time"] + \
                                 self.capacity["burger_ass_time"] + \
                                 self.capacity["burger_pack_time"]
        self.limit_time = limit_time
        self.calculate_max_burger_number_based_on_limit_time()

    def process_order(self, order):
        self.store_current_state_of_burger_capacity_and_inventory()
        order_process_time = datetime.now().replace(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) #initial time
        burgers, order_time = self.extract_burgers_and_time_from_order(order)
        if len(burgers) > self.max_burger:
            return self.log_rejected_order(order)
        for burger in burgers:
            if not self.is_burger_inventory_has_capacity(burger[0]): #first character of burger is burger_type if veggie
                self.restore_prev_state_of_burger_inventory()
                return self.log_rejected_order(order)
            for material in burger:
                if material == "V": #veggie burger, not meterial, its burger_type
                    continue
                if not self.is_material_inventory_has_capacity(material):
                    self.restore_prev_state_of_burger_inventory()
                    return self.log_rejected_order(order)
            # start the process
            burger_process_time = self.calculate_burger_process_time(order_time)
            if burger_process_time > order_process_time: # set the longer burger time as order time, burgers of one order is processed in parallel
                order_process_time = burger_process_time
            self.increase_burger_capacity_waiting_time(order_time) # allocate the burger resource
        order_process_duration = (order_process_time - order_time).seconds/60
        if order_process_duration > self.limit_time:
            self.restore_prev_state_of_burger_capacity()
            self.restore_prev_state_of_burger_inventory()
            return self.log_rejected_order(order)

        self.add_order_process_time_to_total_time(order_process_duration)
        return self.log_accepted_order(order, order_process_duration)

    def preprocess_capacity(self):
        self.capacity_values = [int(var) if var.isdigit() else int(var[:-1]) for var in
                                  self.capacity.split(",")[1:]]
        self.capacity = dict(zip(kitchen_capacity_keys, self.capacity_values))
        dt = datetime.now()
        zero_time = dt.replace(year=1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        self.burger_cook_available_time = numpy.repeat(zero_time, self.capacity["burger_cook_cap"])
        self.burger_ass_available_time = numpy.repeat(zero_time, self.capacity["burger_ass_cap"])
        self.burger_pack_available_time = numpy.repeat(zero_time, self.capacity["burger_pack_cap"])

    @staticmethod
    def extract_burgers_and_time_from_order(order):
        order = order.split(",")
        order_time = datetime.strptime(order[1], "%Y-%m-%d %H:%M:%S")
        return order[3:], order_time

    def get_inventories_state(self):
        return f'{self.capacity["inventory_burger"]},' \
               f'{self.capacity["inventory_lettuce"]},{self.capacity["inventory_tomato"]},' \
               f'{self.capacity["inventory_veggie"]},{self.capacity["inventory_bacon"]}'

    def get_total_process_time(self):
        return self.total_process_time

    def is_burger_inventory_has_capacity(self, burger_type):
        if burger_type == "V":  # veggie burger
            if self.capacity["inventory_veggie"] == 0:
                return False
            self.capacity["inventory_veggie"] -= 1
        else:  # burger
            if self.capacity["inventory_burger"] == 0:
                return False
            self.capacity["inventory_burger"] -= 1
        return True

    def is_material_inventory_has_capacity(self, material):
        if self.capacity[inventory_material_mapping[material]] == 0:
            return False
        self.capacity[inventory_material_mapping[material]] -= 1
        return True

    def calculate_burger_process_time(self, order_time):
        burger_process_time = self.burger_process_time
        burger_cook_waiting_time = 0 if order_time>=self.burger_cook_available_time[0] else (self.burger_cook_available_time[0]-order_time).seconds/60
        burger_ass_waiting_time = 0 if order_time>=self.burger_ass_available_time[0] else (self.burger_ass_available_time[0]-order_time).seconds/60
        burger_pack_waiting_time = 0 if order_time>=self.burger_pack_available_time[0] else (self.burger_pack_available_time[0]-order_time).seconds/60
        burger_process_time += burger_ass_waiting_time + burger_cook_waiting_time + burger_pack_waiting_time
        return order_time + timedelta(minutes=burger_process_time)

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

    def increase_burger_capacity_waiting_time(self, order_time):
        if self.burger_cook_available_time[0].year == 1: #initial value
            self.burger_cook_available_time[0] = order_time
        self.burger_cook_available_time[0] += timedelta(minutes=self.capacity["burger_cook_time"])
        self.burger_cook_available_time = sorted(self.burger_cook_available_time)

        if self.burger_ass_available_time[0].year == 1: #initial value
            self.burger_ass_available_time[0] = order_time
        self.burger_ass_available_time[0] += timedelta(minutes=self.capacity["burger_ass_time"])
        self.burger_ass_available_time = sorted(self.burger_ass_available_time)

        if self.burger_pack_available_time[0].year == 1: #initial value
            self.burger_pack_available_time[0] = order_time
        self.burger_pack_available_time[0] += timedelta(minutes=self.capacity["burger_pack_time"])
        self.burger_pack_available_time = sorted(self.burger_pack_available_time)

    def store_current_state_of_burger_capacity_and_inventory(self):
        self.inventory_burger_state = self.capacity["inventory_burger"]
        self.inventory_lettuce_state = self.capacity["inventory_lettuce"]
        self.inventory_tomato_state = self.capacity["inventory_tomato"]
        self.inventory_veggie_state = self.capacity["inventory_veggie"]
        self.inventory_bacon_state = self.capacity["inventory_bacon"]
        self.burger_cook_state = self.burger_cook_available_time
        self.burger_ass_state = self.burger_ass_available_time
        self.burger_pack_state = self.burger_pack_available_time

    def restore_prev_state_of_burger_capacity(self):
         self.burger_cook_available_time = sorted(self.burger_cook_state)
         self.burger_ass_available_time = sorted(self.burger_ass_state)
         self.burger_pack_available_time = sorted(self.burger_pack_state)

    def restore_prev_state_of_burger_inventory(self):
        self.capacity["inventory_burger"] = self.inventory_burger_state
        self.capacity["inventory_lettuce"] = self.inventory_lettuce_state
        self.capacity["inventory_tomato"] = self.inventory_tomato_state
        self.capacity["inventory_veggie"] = self.inventory_veggie_state
        self.capacity["inventory_bacon"] = self.inventory_bacon_state

    def calculate_max_burger_number_based_on_limit_time(self):
        self.max_burger = self.limit_time/self.burger_process_time
