from collections import Counter
import unittest

class PricingCalculator:
    def __init__(self,products,offers):
        self.products =  {product.name: product for product in products} #make it a dictionary for quicker retrieval
        self.offers = {offer.name: offer for offer in offers}

    # Calculates the subtotal first and then applies discounts
    def calculate(self,basket):
        subtotal=0

        simplified_counts = Counter()

        for entry in basket:
            item_name, qty = entry.split(":")

            qty = float(qty)
            if item_name in self.products:
                product = self.products[item_name]
                # If unit-based (e.g., kg), multiply price by weight
                simplified_counts[item_name] += 1
                if product.unit == 'kg':
                    subtotal += product.price * qty
                else:
                    subtotal += product.price

        # discounts
        total_savings = 0.0
        applied_discounts = {}

        # loop over each discount object in offers
        for disc in self.offers:
            disc = self.offers.get(disc)  # get discount that matches the name
            if not disc:  # avoids needing to run a loop to check if an item is in the dictionary compared to a list
                continue
            discount_amount = round(disc.calculate_discount(self.products, simplified_counts),2) #prevents 0.39999.. aka recurring numbers
            if discount_amount > 0:
                total_savings += discount_amount
                discount_label = f"{disc.name} {disc.amountToGetDiscount} for "
                if disc.rule == 'price':
                    discount_label += f"£{disc.amount:.2f}"
                else:
                    discount_label += f"{disc.amount}"
                applied_discounts[discount_label] = -discount_amount


        total_to_pay = subtotal - total_savings

        self.print_receipt(basket, subtotal, applied_discounts, total_savings, total_to_pay)
        return round(total_to_pay,3) #for testing



    def print_receipt(self, basket, subtotal, applied_discounts, savings, total_to_pay):
        print("Item".ljust(15) + "Price")
        for entry in basket:
            item_name, qty = entry.split(":")
            qty = float(qty)
            if item_name in self.products:

                if self.products[item_name].unit=='each': # if the item isnt based on per kg
                    qty=1
                print(f"{item_name} ({qty}):".ljust(15) + f"{self.products[item_name].price * qty:.2f}")

        # neater formatting
        print("-" * 25)
        print("Subtotal".ljust(15) + f"{subtotal:.2f}")
        print("Savings")
        for discount, amount in applied_discounts.items():
            print("{"+discount.ljust(15)+"} " + f"{amount:.2f}")
        print("Total savings".ljust(15) + f"{-savings:.2f}")
        print("Total to Pay".ljust(15) + f"{total_to_pay:.2f}")



class Product:
    """
    Name: Name of the product
    Price: How much that product will cost
    Unit: Is it priced per unit or per weight?
    """
    def __init__(self, name, price, unit='each'):
        self.name = name
        self.price = price
        self.unit = unit

class Discount:
    """
    Name: Name of the item to be given a discount
    AmountToGetDiscount: How much you need to match the rule
    Amount: Either how much you end up paying per price or per product amount to save
    Rule: Either pay on the amount saving e.g. 3 for 2 means you buy 3 products but only pay for 2 rule here is item
    otherwise its price so you pay £2
    Products: Optional argument if needed to have multiple items to match criteria
    """
    def __init__(self, name, amountToGetDiscount,amount, rule,products=[]):
        #Either e.g 3 beans for price of 2 RULE=ITEM
        # OR e.g 2 cokes for £1 RULE=PRICE
        self.name = name
        self.amountToGetDiscount= amountToGetDiscount
        self.rule = rule
        self.amount=amount
        self.products = products #e.g. For a group of specific items that results in a discount such as 3 specific ales for price/amount of 6


    def calculate_discount_single_product(self, price_per_unit, item_count):
        """
        Handles the simpler case: a discount for exactly one product (like "Beans 3 for 2").
        """
        if self.rule == 'item':
            # e.g. "3 for 2" .. if you have 6 items, you can get that discount twice
            discount_groups = item_count // self.amountToGetDiscount

            discount_per_group = (self.amountToGetDiscount - self.amount) * price_per_unit
            return discount_groups * discount_per_group

        elif self.rule == 'price':
            # e.g. "2 Coke for £1" .. if each Coke is 0.70 normal, then
            # the group of 2 would cost (2 * 0.70) = 1.40 normally
            # the discount price is 1.00 exactly since we defined this in discounts
            # so the discount is 0.40 for each 2-pack
            discount_groups = item_count // self.amountToGetDiscount
            normal_price_for_group = price_per_unit * self.amountToGetDiscount
            discount_per_group = normal_price_for_group - self.amount
            return discount_groups * discount_per_group

        return 0.0

    def calculate_discount_multi_product(self, products_dict, simplified_counts):
        """
        Handles the "multi-product" discount, e.g. "Any 3 ales [Ale1, Ale2, Ale3] for £6".
        :param products_dict: dict of product_name .. Product object
        :param simplified_counts: dict of product_name .. how many purchased
        :return: total discount amount
        """
        # count how many total 'eligible' items we have
        total_eligible_count = 0
        total_eligible_price = 0.0

        # sum up all items that are part of this discount's "products" list
        for p_name in self.products:
            count_for_this_product = simplified_counts.get(p_name, 0)
            total_eligible_count += count_for_this_product
            # Add that many at that product's price
            product_price = products_dict[p_name].price
            total_eligible_price += count_for_this_product * product_price

        # Groups?
        discount_groups = total_eligible_count // self.amountToGetDiscount
        if discount_groups == 0:
            return 0.0

        if self.rule == 'price':
            # example: "Any 3 ales for £6".

            # we can approximate by an average price if they differ
            average_price = total_eligible_price / total_eligible_count
            normal_price_for_one_group = average_price * self.amountToGetDiscount
            discount_per_group = normal_price_for_one_group - self.amount
            total_discount = discount_groups * discount_per_group
            return total_discount

        elif self.rule == 'item':
            # example: "Any 3 from [ProductA, ProductB] for the cost of 2"
            # if each is the same price, it's easy
            average_price = total_eligible_price / total_eligible_count
            # so effectively "3 for 2" means we skip 1 item price for each group
            discount_per_group = (self.amountToGetDiscount - self.amount) * average_price
            total_discount = discount_groups * discount_per_group
            return total_discount

        return 0.0



    def calculate_discount(self, products_dict, simplified_counts):
        """
        Main entry point for calculating the discount this object represents
        Return how much money is saved in total for the given basket
        """
        # if we have a non-empty "products" list, this discount covers multiple different items
        # (e.g. "Ale1", "Ale2", "Ale3" for a '3 for £6' deal)
        if self.products:
            return self.calculate_discount_multi_product(products_dict, simplified_counts)

        # Otherwise, it's a single-product discount look up the discount by `name`
        else:
            item_count = simplified_counts.get(self.name, 0)
            # For single-product discount, we just look up its price
            price_per_unit = products_dict[self.name].price
            return self.calculate_discount_single_product(price_per_unit, item_count)


class TestPricingCalculator(unittest.TestCase):
    def setUp(self):
        """
        Set up the products and offers
        """
        self.products = [

            Product("Beans", 0.50),
            Product("Coke", 0.7),
            Product("Oranges", 1.99, unit='kg'),  # price per kg
            Product("Ale1", 2.50),
            Product("Ale2", 2.50),
            Product("Ale3", 2.50),
            Product("Ale4", 2.50),
        ]
        # Define special offers NAMING is important MUST be consistent with above
        self.offers = [
            Discount("Beans", 3, 2, rule='item'),
            Discount("Coke", 2, 1, rule='price'),
            Discount("Ale", 3, 6, rule='price', products=["Ale1", "Ale2", "Ale3"])

        ]
        self.calculator = PricingCalculator(self.products, self.offers)

    def test_beans_discount_normal(self):
        """
        Test-cases : - Exactly as it says, have 3 beans with price of 0.5 per each so we expect final price to be 1
        """
        basket = ["Beans:1", "Beans:1", "Beans:1"]
        expected_total = 1
        self.assertEqual(self.calculator.calculate(basket), expected_total)
    def test_beans_discount_more(self):
        """
        What if there is more than the expected 3? (4 here)
        """
        basket = ["Beans:1", "Beans:1", "Beans:1","Beans:0.5"]
        expected_total = 1.5
        self.assertEqual(self.calculator.calculate(basket), expected_total)
    def test_beans_discount_less(self):
        """
        What if there is less than the expected 3? (2 here)
        """
        basket = ["Beans:1", "Beans:1"]
        expected_total = 1
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_oranges_discount_normal(self):
        """
        What if there Oranges are at 1 kilo, since they are at £1.99/kg
        """
        basket = ["Oranges:1"]
        expected_total = 1.99
        self.assertEqual(self.calculator.calculate(basket), expected_total)
    def test_oranges_discount_less(self):
        """
        What if there Oranges are at 0.1 kilo, since they are at £1.99/kg
        """
        basket = ["Oranges:0.1"]
        expected_total = 0.199
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_oranges_discount_more(self):
        """
        What if there Oranges are at 10 kilo, since they are at £1.99/kg
        """
        basket = ["Oranges:10"]
        expected_total = 19.9
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_coke_discount_normal(self):
        """
        What if there Coke is at 0.7 and we have 2? Mixed the weight up too
        """
        basket = ["Coke:1","Coke:0.5"]
        expected_total =1
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_coke_discount_more(self):
        """
        What if there Coke is at 0.7 and we have 4? Mixed the weight up too
        """
        basket = ["Coke:1","Coke:0.5","Coke:0.1","Coke:10"]
        expected_total =2
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_coke_discount_less(self):
        """
        What if there Coke is at 0.7 and we have 1? No discount to be expected
        """
        basket = ["Coke:1"]
        expected_total =0.7
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_ale_discount_normal(self):
        """
        What if we have the correct Ale's and the weight is mixed up?
        """
        basket = ["Ale1:1","Ale2:0.5","Ale3:0.5"]
        expected_total =6
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_ale_discount_more(self):
        """
        What if we have multiple Ale? It should give the discount for 3 but not 4
        """
        basket = ["Ale1:1","Ale2:0.5","Ale3:0.5","Ale1:0.1"]
        expected_total =8.50
        self.assertEqual(self.calculator.calculate(basket), expected_total)

    def test_ale_discount_less(self):
        """
        What if we have less Ale? It should not give a discount
        """
        basket = ["Ale1:1","Ale2:0.5"]
        expected_total =5
        self.assertEqual(self.calculator.calculate(basket), expected_total)




if __name__ == "__main__":
    """
        BASKET LOGIC - Item:Weight , weight is needed so products priced per weight can calculated also allows for easy modifications to per weight or per unit
        PRODUCT LOGIC - Arguments are the Item Name, followed by price, default rule is that its priced per item, specify 'kg' otherwise
        OFFER LOGIC - Item name, amount to get a discount, offer (either e.g. X for 2 as in the price for two of that item OR X for £2 as in money) this rule
        is indicated by the 'rule' parameter. Also you can give it multiple products to indicate that its multiple products to get that discount.
        
    """
    products = [

        Product("Beans", 0.50),
        Product("Coke", 0.7),
        Product("Oranges", 1.99, unit='kg'),  # price per kg
        Product("Ale1", 2.50),
        Product("Ale2", 2.50),
        Product("Ale3", 2.50),
        Product("Ale4",2.50),
    ]
    # Define special offers NAMING is important MUST be consistent with above
    offers = [
        Discount("Beans", 3, 2, rule='item'),
        Discount("Coke", 2, 1, rule='price'),
        Discount("Ale", 3, 6, rule='price', products=["Ale1", "Ale2", "Ale3"])

    ]


    """
    Runs the unit tests, insert a '#' in front to stop it from running 
    e.g. # unittest.main
    """
    # unittest.main()

    """
    Demonstrating the shopping cart working with multiple products, comment out the unit tests for visual clarity
    """
    basket = ["Beans:1","Oranges:1","Beans:1","Beans:0.5","Coke:1","Coke:1",]
    calculator = PricingCalculator(products, offers)
    calculator.calculate(basket)
