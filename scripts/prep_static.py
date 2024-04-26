from json import load
from pathlib import Path

with open("data-gen.json", "r") as f:
    data = load(f)
    r = Path("imgs")
    r.mkdir()
    for restaurant in data["restaurants"]:
        p = r / Path(restaurant)
        p.mkdir()
        for item in data["restaurants"][restaurant]["menu"]:
            m = p / item
            m.mkdir()
