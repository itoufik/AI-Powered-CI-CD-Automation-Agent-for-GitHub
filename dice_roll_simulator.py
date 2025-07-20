import random
from collections import defaultdict

# Menu instructions
def print_menu():
    print("\n🎲 Dice Roll Simulator")
    print("1. Roll one die")
    print("2. Roll two dice")
    print("3. View stats")
    print("4. Reset stats")
    print("5. Exit")

# Dice statistics tracker
class DiceStats:
    def __init__(self):
        self.single_die_rolls = defaultdict(int)
        self.double_die_rolls = defaultdict(int)
        self.total_single = 0
        self.total_double = 0

    def record_single(self, value):
        self.single_die_rolls[value] += 1
        self.total_single += 1

    def record_double(self, total):
        self.double_die_rolls[total] += 1
        self.total_double += 1

    def reset(self):
        self.__init__()

    def print_stats(self):
        print("\n🎯 Roll Statistics:")
        if self.total_single == 0 and self.total_double == 0:
            print("No rolls yet!")
            return

        if self.total_single:
            print(f"\n- Single Die Rolls ({self.total_single} total):")
            for i in range(1, 7):
                count = self.single_die_rolls[i]
                percent = (count / self.total_single) * 100 if self.total_single else 0
                print(f"  {i}: {count} times ({percent:.1f}%)")

        if self.total_double:
            print(f"\n- Two Dice Rolls ({self.total_double} total):")
            for total in range(2, 13):
                count = self.double_die_rolls[total]
                percent = (count / self.total_double) * 100 if self.total_double else 0
                print(f"  {total}: {count} times ({percent:.1f}%)")
        print("")

# Rolling logic
def roll_one_die(stats: DiceStats):
    print("\nRolling one die...")
    value = random.randint(1, 6)
    print(f"🎲 You rolled a {value}")
    stats.record_single(value)

def roll_two_dice(stats: DiceStats):
    print("\nRolling two dice...")
    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    total = d1 + d2
    print(f"🎲 You rolled a {d1} and a {d2} (Total: {total})")
    stats.record_double(total)

# Main loop
def main():
    stats = DiceStats()
    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            roll_one_die(stats)
        elif choice == "2":
            roll_two_dice(stats)
        elif choice == "3":
            stats.print_stats()
        elif choice == "4":
            stats.reset()
            print("🔄 Stats reset.")
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❗ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
