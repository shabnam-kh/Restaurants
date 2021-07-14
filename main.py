from builtins import open

from inventory import Inventory


with open('input.txt') as reader:
    i=0
    for line in reader.readlines():
        line = line.rstrip()
        if i==0: # first line is
            Inventory = Inventory(branch_capacity=line)
        else:
            print(Inventory.process_order(order=line))
        i+=1

    print("R1", ",", "TOTAL", ",", Inventory.get_total_process_time())
    print("R1", ",",  "INVENTORY", ",", Inventory.get_inventories_state())
