from builtins import len
from unittest import TestCase
from ..inventory import Inventory

branch_inventory_capacity = "R1,4C,1,3A,2,2P,1,100,200,200,100,100"
order = "R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT"
inventory = Inventory(branch_inventory_capacity)


class InventoryTest(TestCase):


    def test_preprocess_branch_inventory_capacity_should_extract_values_correctly(self):

        self.assertEqual(inventory.branch_capacity["burger_cook_cap"], 4)
        self.assertEqual(inventory.branch_capacity["burger_ass_cap"], 3)
        self.assertEqual(inventory.branch_capacity["burger_pack_cap"], 2)

        self.assertEqual(inventory.branch_capacity["inventory_burger_cap"],100)
        self.assertEqual(inventory.branch_capacity["inventory_lettuce_cap"], 200)
        self.assertEqual(inventory.branch_capacity["inventory_tomato_cap"], 200)
        self.assertEqual(inventory.branch_capacity["inventory_veggie_cap"], 100)
        self.assertEqual(inventory.branch_capacity["inventory_bacon_cap"], 100)

    def test_extract_foods_list_from_order(self):
        foods = inventory.extract_foods_list_from_order(order)
        self.assertEqual(foods[0], "BLT")
        self.assertEqual(foods[1], "LT")
        self.assertEqual(foods[2], "VLT")

    def test_is_burger_inventory_has_capacity(self):
        _inventory = Inventory(branch_inventory_capacity)
        _inventory.branch_capacity["inventory_veggie_cap"] = 0

        self.assertFalse(_inventory.is_burger_inventory_has_capacity("V"))

        _inventory.branch_capacity["inventory_burger_cap"] = 0

        self.assertFalse(_inventory.is_burger_inventory_has_capacity("B"))

        _inventory.branch_capacity["inventory_veggie_cap"] = 1

        self.assertTrue(_inventory.is_burger_inventory_has_capacity("V"))
        self.assertEqual(_inventory.branch_capacity["inventory_veggie_cap"] , 0)

        _inventory.branch_capacity["inventory_burger_cap"] = 1

        self.assertTrue(_inventory.is_burger_inventory_has_capacity("B"))
        self.assertEqual(_inventory.branch_capacity["inventory_burger_cap"], 0)

    def test_is_material_inventory_has_capacity(self):
        _inventory = Inventory(branch_inventory_capacity)
        _inventory.branch_capacity["inventory_lettuce_cap"] = 0

        self.assertFalse(_inventory.is_material_inventory_has_capacity("L"))

        _inventory.branch_capacity["inventory_lettuce_cap"] = 1

        self.assertTrue(_inventory.is_material_inventory_has_capacity("L"))
        self.assertEqual(_inventory.branch_capacity["inventory_lettuce_cap"] , 0)

    def test_add_order_process_time_to_total_time(self):
        self.assertEqual(inventory.total_process_time, 0)
        inventory.add_order_process_time_to_total_time(5)
        self.assertEqual(inventory.total_process_time, 5)

    def test_increase_burger_capacity_waiting_time(self):
        inventory.increase_burger_capacity_waiting_time()

        self.assertEqual(len(inventory.burger_cook_cap), 4)
        self.assertEqual(inventory.burger_cook_cap[0],0)
        self.assertEqual(inventory.burger_cook_cap[-1],
                         inventory.branch_capacity["burger_cook_time"])

    def test_process_order_should_reject_orders_when_burgers_more_than_max_number(self):
        _order = 'R1,2020-12-08 19:15:32,O2,VLT,VT,BLT,LT,VLT'
        self.assertEqual(inventory.process_order(_order), 'R1,O2,REJECTED')

    def test_process_order_should_reject_orders_when_no_inventory_capacity(self):
        inventory_capacity = "R1,4C,1,3A,2,2P,1,0,200,200,100,100"
        _order = "R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT"
        _inventory = Inventory(inventory_capacity)
        self.assertEqual(_inventory.process_order(_order), 'R1,ORDER1,REJECTED')

        inventory_capacity = "R1,4C,1,3A,2,2P,1,100,0,200,100,100"
        _inventory = Inventory(inventory_capacity)
        self.assertEqual(_inventory.process_order(_order), 'R1,ORDER1,REJECTED')


