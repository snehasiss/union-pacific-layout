#!/usr/bin/env python3

# test of Locomotive and Roster
# filename: test.py


from locomotive import Locomotive
from roster import Roster

def main():
	roster = Roster.from_csv("steam.csv")

	breakpoint()

	locomotive = roster.find(4014)

	breakpoint()
	print("running")
	print(locomotive)
	print("completed")

# --- main ---
if __name__ == "__main__":
	main()

## end

