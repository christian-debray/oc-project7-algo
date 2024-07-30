# oc-project7-algo
OC project 7 algorithm

2 algorithms solving an optimization problem


**Brute force solution:**

```
    python bruteforce.py
```
Will load data from optimized.py data/actions_data.csv.

This is hardcoded, as it woudn't make much sense to try the brute force solution on larger datasets...

**Optimized solution**

Uses a genetic algorithm.

  - Works with any csv file (see the sample files in data/ folder for data formats)
  - Accepts parameters:
     - population size (defaults to 100, worth increasing for large datasets)
     - maximum generations (defaults to 50, which should be fine)
     - attempts : how often the algorithms should run. The more attempts, the better the solution, but longer execution time...

```
    usage: optimized.py [-h] [--pop-size [POP_SIZE]] [--max-gen [MAX_GEN]] [--attempts [ATTEMPTS]] [--max-value [MAX_VALUE]] datafile
```
for ex.:

```
    optimized.py data/actions_data.csv
```

List all options:
```
    python optimized.py --help
```
