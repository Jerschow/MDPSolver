# MDPSolver
Markovian Decision Problem Solver.

List value of node:
nodename=8
List probabilities of chance node:
nodename % probval1 probval2 ... probvaln
Listing probabilities of decision node is same as chance but you only list the prob of getting to your desired destination
List edges:
nodename: [edge1,edge2,...]

how to run:
python3 interface.py -df val -iter val -tol val -min inputfile.txt
where -df -iter -tol and -min are optional flags signifying discount factor, max iterations, tolerance and minimize (instead of maximize) respectively.
