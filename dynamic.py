import argparse
import csv
from pathlib import Path
import os
import time


# Python3 code for Dynamic Programming
# based solution for 0-1 Knapsack problem


# Prints the items which are put in a
# knapsack of capacity W
def printknapSack(W, wt, val, n):
    K = [[0 for w in range(W + 1)] for i in range(n + 1)]

    # Build table K[][] in bottom
    # up manner
    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
            elif wt[i - 1] <= w:
                K[i][w] = max(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w])
            else:
                K[i][w] = K[i - 1][w]

    # stores the result of Knapsack
    res = K[n][W]
    print(res)

    w = W
    for i in range(n, 0, -1):
        if res <= 0:
            break
        # either the result comes from the
        # top (K[i-1][w]) or from (val[i-1]
        # + K[i-1] [w-wt[i-1]]) as in Knapsack
        # table. If it comes from the latter
        # one/ it means the item is included.
        if res == K[i - 1][w]:
            continue
        else:

            # This item is included.
            yield (i-1, wt[i - 1])

            # Since this weight is included
            # its value is deducted
            res = res - val[i - 1]
            w = w - wt[i - 1]


def parse_args():
    p = argparse.ArgumentParser("genetics_demo")
    p.add_argument("csv_file", nargs="?", default="")
    p.add_argument("--export-data")
    p.add_argument("--import-data")
    args = p.parse_args()
    csv_file = None
    export_data = None
    import_data = None
    if args.csv_file:
        csv_file = make_file(args.csv_file)
    if args.import_data:
        import_data = make_file(args.import_data)
    elif args.export_data:
        export_data = make_file(args.export_data)
    return (csv_file, import_data, export_data)


def make_file(file_n: str) -> Path:
    """create or touch a file"""
    f = Path(Path(os.getcwd()), file_n).absolute()
    if not f.exists():
        if not f.parent.exists():
            f.parent.mkdir(mode=0o777, parents=True)
        f.touch(mode=0o666)
    return f


(csv_file, import_data, export_data) = parse_args()
names = []
items_weight = []
items_value = []
if import_data:
    print(f"Importing data from {import_data}...")
    items_weight = []
    items_value = []
    with open(import_data, "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                val = float(row[1])
                profit = float(row[2])
                if val > 0 and profit > 0:
                    names.append(row[0])
                    items_weight.append(int(100*val))
                    items_value.append(int((profit * val)))
            except ValueError:
                pass

# Driver code
val = [60, 100, 120]
wt = [10, 20, 30]
W = 50
n = len(val)

val = items_value
wt = items_weight
W = 500*100
n = len(val)

start = time.perf_counter()
for (i, w) in printknapSack(W, wt, val, n):
    print(names[i], i, w)
ellapsed = time.perf_counter() - start
print(f"Dynamic algorithm done in {round(ellapsed, 3)} seconds")