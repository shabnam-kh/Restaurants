from builtins import open

from kitchen import Kitchen


with open('input.txt') as reader:
    i=0
    for line in reader.readlines():
        line = line.rstrip()
        if i==0: # first line is
            kitchen = Kitchen(capacity=line)
        else:
            print(kitchen.process_order(order=line))
        i+=1

    print("R1", ",", "TOTAL", ",", kitchen.get_total_process_time())
    print("R1", ",",  "INVENTORY", ",", kitchen.get_inventories_state())
