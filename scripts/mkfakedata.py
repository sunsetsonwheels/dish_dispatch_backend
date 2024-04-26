from faker import Faker
from faker.providers import address, credit_card, phone_number, currency
from faker_food import FoodProvider
from json import dump

fake = Faker("en_AU")
fake.add_provider(address)
fake.add_provider(credit_card)
fake.add_provider(phone_number)
fake.add_provider(currency)
fake.add_provider(FoodProvider)

data = {
    "customers": {},
    "restaurants": {}
}

for _ in range(5):
    data["customers"][fake.phone_number()] = {
        "name": fake.name(),
        "address": fake.address(),
        "credit_card": {
            "number": fake.credit_card_number("mastercard"),
            "code": fake.credit_card_security_code("mastercard"),
            "expiry": fake.credit_card_expire()
        },
        "membership_number": None,
        "password": "1234"
    }

for _ in range(10):
    data["restaurants"][fake.phone_number()] = {
        "name": "",
        "cuisine": "",
        "address": fake.address(),
        "menu": {},
        "orders": [{"items": [{} for _ in range(fake.random_int(min=1, max=3))], "customer": list(data["customers"]), "note": None, "status": "preparing"} for _ in range(2)]
    }

with open("data.json", "w") as data_file:
    dump(data, data_file, indent=4)