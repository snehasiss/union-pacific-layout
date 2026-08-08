#!/usr/bin/env python3

# test of Locomotive and Roster
# filename: test.py


from libs.locomotive import Locomotive
from libs.roster import Roster
from libs.dataclassfactory import DataclassFactory

def main():
	roster = Roster.from_csv("steam.csv")

	#breakpoint()

	locomotive = roster.find(4014)

	#breakpoint()
	print("running")
	print(locomotive)
	print("completed")

	roster.save()

# --- main ---
if __name__ == "__main__":
	main()

## end

