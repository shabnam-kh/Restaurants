from builtins import len
from unittest import TestCase
from kitchen import Kitchen
from datetime import datetime, timedelta

inventory_capacity = "R1,4C,1,3A,2,2P,1,100,200,200,100,100"
order = "R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT"
kitchen = Kitchen(inventory_capacity)


class KitchenTest(TestCase):


    def test_preprocess_capacity_should_extract_values_correctly(self):

        self.assertEqual(kitchen.capacity["burger_cook_cap"], 4)
        self.assertEqual(kitchen.capacity["burger_ass_cap"], 3)
        self.assertEqual(kitchen.capacity["burger_pack_cap"], 2)

        self.assertEqual(kitchen.capacity["inventory_burger"],100)
        self.assertEqual(kitchen.capacity["inventory_lettuce"], 200)
        self.assertEqual(kitchen.capacity["inventory_tomato"], 200)
        self.assertEqual(kitchen.capacity["inventory_veggie"], 100)
        self.assertEqual(kitchen.capacity["inventory_bacon"], 100)

    def tes_extract_burgers_and_time_from_order(self):
        burgers = kitchen.extract_burgers_and_time_from_order(order)
        self.assertEqual(burgers[0], "BLT")
        self.assertEqual(burgers[1], "LT")
        self.assertEqual(burgers[2], "VLT")

    def test_is_burger_inventory_has_capacity(self):
        _kitchen = Kitchen(inventory_capacity)
        _kitchen.capacity["inventory_veggie"] = 0

        self.assertFalse(_kitchen.is_burger_inventory_has_capacity("V"))

        _kitchen.capacity["inventory_burger"] = 0

        self.assertFalse(_kitchen.is_burger_inventory_has_capacity("B"))

        _kitchen.capacity["inventory_veggie"] = 1

        self.assertTrue(_kitchen.is_burger_inventory_has_capacity("V"))
        self.assertEqual(_kitchen.capacity["inventory_veggie"] , 0)

        _kitchen.capacity["inventory_burger"] = 1

        self.assertTrue(_kitchen.is_burger_inventory_has_capacity("B"))
        self.assertEqual(_kitchen.capacity["inventory_burger"], 0)

    def test_is_material_inventory_has_capacity(self):
        _kitchen = Kitchen(inventory_capacity)
        _kitchen.capacity["inventory_lettuce"] = 0

        self.assertFalse(_kitchen.is_material_inventory_has_capacity("L"))

        _kitchen.capacity["inventory_lettuce"] = 1

        self.assertTrue(_kitchen.is_material_inventory_has_capacity("L"))
        self.assertEqual(_kitchen.capacity["inventory_lettuce"] , 0)

    def test_add_order_process_time_to_total_time(self):
        self.assertEqual(kitchen.total_process_time, 0)
        kitchen.add_order_process_time_to_total_time(5)
        self.assertEqual(kitchen.total_process_time, 5)

    def test_increase_burger_capacity_waiting_time(self):
        burgers, order_time = kitchen.extract_burgers_and_time_from_order(order)
        kitchen.increase_burger_capacity_waiting_time(order_time)

        self.assertEqual(len(kitchen.burger_cook_available_time), 4)
        self.assertEqual(kitchen.burger_cook_available_time[0].year,1)
        self.assertEqual(kitchen.burger_cook_available_time[-1],
                         order_time + timedelta(minutes=kitchen.capacity["burger_cook_time"]))

    def test_process_order_should_reject_orders_when_burgers_more_than_max_number(self):
        _order = 'R1,2020-12-08 19:15:32,O2,VLT,VT,BLT,LT,VLT,LT'
        self.assertEqual(kitchen.process_order(_order), 'R1,O2,REJECTED')

    def test_process_order_should_reject_orders_when_no_inventory_capacity(self):
        inventory_capacity = "R1,4C,1,3A,2,2P,1,0,200,200,100,100"
        _order = "R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT"
        _kitchen = Kitchen(inventory_capacity)
        self.assertEqual(_kitchen.process_order(_order), 'R1,ORDER1,REJECTED')

        inventory_capacity = "R1,4C,1,3A,2,2P,1,100,0,200,100,100"
        _kitchen = Kitchen(inventory_capacity)
        self.assertEqual(_kitchen.process_order(_order), 'R1,ORDER1,REJECTED')

    def test_process_order(self):
        inventory_capacity = "R1,3C,2,2A,5,1P,3,100,200,200,100,100"
        _kitchen = Kitchen(inventory_capacity, limit_time=50)
        order1 = "R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT"
        order2 = "R1,2020-12-08 19:25:17,ORDER2,VT,VLT"
        self.assertEqual(_kitchen.process_order(order1), 'R1,ORDER1,ACCEPTED,21.0')
        self.assertEqual(_kitchen.process_order(order2), 'R1,ORDER2,REJECTED')





