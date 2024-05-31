from pymongo import MongoClient
from urllib.parse import quote
from getpass import getpass

print(f"[Make Dish Dispatch Database]")
print("")
print("WARNING:")
print("This script presumes that you already have an admin account set up.")
print("If not, nope out below and follow the instructions at:")
print("https://docs.mongodb.com/manual/tutorial/configure-scram-client-authentication/")
print("")

conn_str = f"mongodb://\
{quote(input('Enter DB admin username: '))}:{quote(getpass('Enter DB admin password: '))}@{input('Enter DB URL & port (host:port): ')}\
"

client = MongoClient("mongodb://admin:admin@localhost:27017")
db = client.dish_dispatch

db.command(
    "createUser",
    "dish_dispatch",
    pwd="dish_dispatch",
    roles=["readWrite"]
)

print("")
print("Et voila! The database and 'dish_dispatch' database user have been created.")
print("You may now insert data into the database.")