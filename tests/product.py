from dataclasses import dataclass

@dataclass
class Train:
	name: str
	price: float
	quantity: int

item = Train(name='Challenger', price=705, quantity=1)

print (item)
print (item.name)
