from json import load

data = {"customers": [], "restaurants": []}

with open("scripts/data-gen.json", "r") as f:
    data = load(f)

data["cuisines"] = [data["restaurants"][phone]["cuisine"] for phone in data["restaurants"]]