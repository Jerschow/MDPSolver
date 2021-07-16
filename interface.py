import sys
from os import path
import main


DEFAULT_ITERATIONS = 50
DEFAULT_DF = 1
DEFAULT_TOL = .001


maximize = True
fname = df = tol = iterations = None
skip = False
for i in range(len(sys.argv)):
    if sys.argv[i] == "-df":
        try:
            df = float(sys.argv[i + 1])
            if df < 0 or df > 1:
                print("Discount factor should be float between 0 and 1")
                exit(1)
        except ValueError:
            print("Discount factor should be float between 0 and 1")
            exit(1)
        skip = True
    elif sys.argv[i] == "-min":
        maximize = False
    elif sys.argv[i] == "-tol":
        try:
            tol = float(sys.argv[i + 1])
            if tol <= 0:
                print("Tolerance should be float greater than 0")
                exit(1)
        except ValueError:
            print("Tolerance should be float greater than 0")
            exit(1)
        skip = True
    elif sys.argv[i] == "-iter":
        try:
            iterations = int(sys.argv[i + 1])
            if iterations <= 0:
                print("Iterations should be int greater than 0")
                exit(1)
        except ValueError:
            print("Iterations should be int greater than 0")
            exit(1)
        skip = True
    elif sys.argv[i] == "interface.py":
        continue
    else:
        if not skip:
            if fname != None:
                print("Only 1 graph file allowed.")
                exit(1)
            if not path.isfile(sys.argv[i]):
                print("File does not exist: " + sys.argv[i])
                exit(1)
            fname = sys.argv[i]
            skip = False
if df == None:
    df = 1
if tol == None:
    tol = DEFAULT_TOL
if iterations == None:
    iterations = DEFAULT_ITERATIONS
nodes = main.start(fname,tol,iterations,maximize,df)