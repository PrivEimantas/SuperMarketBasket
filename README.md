# SuperMarketBasket


![image](https://github.com/user-attachments/assets/ea7ddb4a-6831-40d3-8662-ff8cbe96596b)


1. Simply run the python file, I developed in PyCharm so you can just right click and run OR run "python CSE_Exercise.py" in a terminal.
2. The basket is based on "Item:Weight" so it is the name of an item followed by how much it weighs in kg.
3. This has been made using Classes for easy future modification (PricingCalculator, Product, Discount, TestPricingCalculator(unittest.TestCase) ).

The first class will calculate the subtotal based on the Products and then discounts based on Discount class, it is designed so that even if prices are changed or discounts, this will be dynamic and still run as expected with the correct output, allowing for easy modification.

Product :- Name, price, unit. The product's names and and prices can be adjusted easily along with whether it is per kg or per unit, so for future if you wanted to sell oranges per unit, you can just type unit='each' and it will be priced per orange rather than weight, same with name or weight.

Discount :- name, amountToGetDiscount,amount, rule,products=[]. This class means we can dynamically calculate discounts **without** needing to hard-code any values so e.g. 3 for 2 can be calculated as 3 items for the price of 2 OR 3 for the price of £2 by just allocating a 'rule' as 'item' or 'price'. Products means you can add items, so multiple products are needed to satisfy a discount offer, this is an optional argument. This also means that if you want to add a completely different product in the future, simply adjust the parameters and it will work.

TestPricingCalculator - Run test units for items with expected prices.

4. At the bottom of the file, if you comment out the " unittest.main()" it will stop running unit tests so you can put items in the basket and see the output more clearly, you can do this by putting a hashtag in front of it.

Code is commented so can be read and understood more if needed.

Thank you for reading and I hope this is suitable! :)
