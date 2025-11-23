import sys

if len(sys.argv) != 2:
    print("Usage: python playvsbot.py <path_to_Q_table_csv>")
    sys.exit(1)

qtable_filename = sys.argv[1]

