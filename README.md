# Restaurants
A multi branch burger joint is trying to find a way to optimise the cooking process to maximise its profitability and reduce the cooking time. 
This burger joint has different branches and each branch comes with a different capacity, Each branch has an inventory to process burgers.
Each order should be processed within 20 minutes else will be rejected. Each order could also get rejected if the branch runs out of inventory.

##Input data
###order
each order comes as a new line of strings formatted in a particular format.

`R1,2020-12-08 21:15:31,ORDER1,BLT,LT,VLT`

input file is exist in main directory as input.txt

###branch capacity
is a new line of strings formatted in a particular format.

`R1,4C,1,3A,2,2P,1,100,200,200,100,100`

##Output
`R1,O1,ACCEPTED,8`

`R1,O2,ACCEPTED,7`

`R1,O3,REJECTED`

`R1,TOTAL,25`

`R1,INVENTORY,58,130,115,63,50`

## Deploy
install the requirments with pip

`pip install -r requirmets.pip`

then run the main script

`python main.py`

## Tests
tests are written with the help of pytest
to run all the tests

`pytest`

to run an individual test

`pytest test_mod.py::TestClass::test_method`
