class Node:
    def __init__(self,name):
        self.name = name
        self.children = []
        self.val = self.probs = self.otherprob = None
        self.decision = self.leaf = self.chance = self.back_to_self = False

    def isLeaf(self):
        return self.children == []

    def appendchild(self,child):
        self.children.append(child)

    def __str__(self):
        return self.name

    def set_otherprob(self):
        if self.back_to_self:
                self.otherprob = (1 - self.probs) / (len(self.children))
        else:
            self.otherprob = (1 - self.probs) / (len(self.children) - 1)

    def check_update_prob(self):
        if self.decision and self.otherprob == None and self.probs != None and len(self.children) != 1:
            self.set_otherprob()
        elif self.probs != None and self.chance and len(self.probs) != len(self.children):
            print("Chance node " + self.name + " has different amounts of edges and probabilities listed")
            exit(1)

    def set_prob(self,probs):
        if len(probs) == 1:
            self.decision = True
            self.probs = probs[0]
            if len(self.children) > 1:
                self.set_otherprob()
        else:
            self.chance = True
            self.probs = probs
            if self.children != [] and len(self.children) != len(self.probs):
                print("Chance node " + self.name + " has different amounts of edges and probabilities listed")
                exit(1)

    def set_val(self,val):
        self.leaf = True
        self.val = val


def readline(rest):
    if rest == "":
        return rest,rest,False
    s = ""
    count = 0
    haspercent = False
    for i in range(len(rest)):
        char = rest[i]
        if char == '\n':
            rest = rest[count + 1:]
            return s,rest,True
        if char != " ":
            s += rest[i]
            if char == "%":
                haspercent = True
        elif haspercent == True:
            s += ","
        count += 1
    rest = rest[count:]
    return s,rest,True

def find(s,chr):
    return s.index(chr)

def findequals(s):
    return find(s,"=")

def findcolon(s):
    return find(s,":")

def beforecolon(s):
    return s[:findcolon(s)]

def beforeequals(s):
    return s[:findequals(s)]

def afterequals(s):
    return float(s[findequals(s) + 1:])

def findpercent(s):
    return find(s,"%")

def beforepercent(s):
    return s[:findpercent(s)]

def afterpercent(s):
    return s[findpercent(s) + 1:]

def getchildren(s):
    return s[findcolon(s) + 2:s.index(']')].split(",")

def get_probs(s,lname):
    lst = s[findpercent(s) + 1:].split(",")
    returnlst = []
    sum = 0
    for i in range(len(lst)):
        if lst[i] != "":
            lst[i] = float(lst[i])
            sum += lst[i]
            if lst[i] > 1 or lst[i] < 0:
                print("Node " + lname + " has invalid probability listed")
                exit(1)
            returnlst.append(lst[i])
    if sum != 1 and len(returnlst) != 1.:
        print("Node " + lname + " has probabilities that do not sum to 1")
        exit(1)
    return returnlst

def to_prob_format(prob):
    return [prob]

def get_parent(nodedict,rootstr):
    pname = beforecolon(rootstr) # get stuff before colon, which is name of vertex
    parent = None
    try:
        parent = nodedict[pname]
    except KeyError:
        parent = nodedict[pname] = Node(pname)
    return parent

def get_children(parent,rootstr):
    cs = getchildren(rootstr)
    for c in cs:
        if c == parent.name:
            parent.back_to_self = True # important for special case of decision node missing and still going back to yourself
        parent.appendchild(c)
    return parent

def check_children(parent,parents):
    if len(parent.children) == 1:
        if parent.probs != 1 and parent.probs != None:
            print("Single edged node " + parent.name + " has multiple provided probabilities or 1 probability != 1")
            exit(1)
        parent.set_prob(to_prob_format(1))
    else:
        parent.check_update_prob()
    parents.append(parent)
    return parents

def handle_children(parent,nodedict,parents,rootstr):
    return nodedict,check_children(get_children(parent,rootstr),parents)

def handle_parent(nodedict,parents,rootstr):
    parent = get_parent(nodedict,rootstr)
    return handle_children(parent,nodedict,parents,rootstr)

def get_leaf(nodedict,rootstr):
    lname = beforeequals(rootstr)
    leaf = None
    try:
        leaf = nodedict[lname]
        leaf.set_val(afterequals(rootstr))
    except KeyError:
        leaf = nodedict[lname] = Node(lname)
        leaf.set_val(afterequals(rootstr))
    return leaf

def handle_leaf(nodedict,leaves,rootstr):
    leaves.append(get_leaf(nodedict,rootstr))
    return nodedict,leaves

def handle_prob_description(nodedict,rootstr):
    lname = beforepercent(rootstr)
    try:
        probs = get_probs(rootstr,lname)
        nodedict[lname].set_prob(probs)
        if len(nodedict[lname].children) == 1 and (len(probs) > 1 or probs[0] != 1):
            print("Single edged node " + lname + " has multiple provided probabilities or 1 probability != 1")
            exit(1)
    except KeyError:
        leaf = nodedict[lname] = Node(lname)
        leaf.set_prob(get_probs(rootstr,lname))
    return nodedict

def handle_nonedge_description(nodedict,leaves,rootstr):
    try: # leaf
        nodedict,leaves = handle_leaf(nodedict,leaves,rootstr)
    except ValueError: # probability description
        nodedict = handle_prob_description(nodedict,rootstr)
    return nodedict,leaves

def handle(nodedict,parents,leaves,rootstr,f):
    if rootstr != "" and rootstr[0] != "#":
        try: # internal node
            nodedict,parents = handle_parent(nodedict,parents,rootstr)
        except ValueError: # leaf or probability description
            nodedict,leaves = handle_nonedge_description(nodedict,leaves,rootstr)
    rootstr,f,cont = readline(f)
    return nodedict,parents,leaves,rootstr,f,cont

def check_parents(nodedict,parents):
    keys = nodedict.keys()
    for p in parents:
        if p.probs == None:
            p.set_prob(to_prob_format(1))
        for i in p.children:
            if i not in keys:
                nodedict[i] = Node(i) # If not listed but listed as an edge, the node is a leaf with reward 0
                nodedict[i].set_val(0)
        if (isinstance(p.probs,list) or (p.probs != 1 and p.probs != None)) and len(p.children) == 1:
            print("Single edged node " + p.name + " has multiple provided probabilities or 1 probability != 1")
            exit(1)
    return nodedict

def check_leaves(leaves):
    for l in leaves:
        if l.probs != None and l.children == []:
            print("Leaf " + l.name + " has no edges but a probability specification. Error.")
            exit(1)

def cleanup(nodedict,leaves,parents):
    check_leaves(leaves)
    return check_parents(nodedict,parents)

def parse(fname):
    nodedict = {}
    f = open(fname,"r").read() # needs to be changed
    rootstr,f,cont = readline(f)
    parents = []
    leaves = []
    while rootstr != '' or cont:
        nodedict,parents,leaves,rootstr,f,cont = handle(nodedict,parents,leaves,rootstr,f)
    return cleanup(nodedict,leaves,parents)

def check(nodedict):
    possible_roots = list(nodedict.keys())
    for node in nodedict:
        for c in nodedict[node].children:
            try:
                possible_roots.remove(c)
            except ValueError: # already removed
                pass
            try:
                nodedict[c]
            except KeyError:
                print("Missing node '" + c + "' referenced as child in node '" + node + "'")
                exit(1)
    if len(possible_roots) == 0:
        print("No root")
        exit(1)
    if len(possible_roots) > 1:
        print("Multiple root-like nodes: " + str(possible_roots))
        exit(1)
    return nodedict[possible_roots[0]]

def print_parsed_graph(nodedict):
    for i in nodedict.keys():
        if nodedict[i].decision:
            print(i)
            print("Decisions")
            print(nodedict[i].probs)
            print(nodedict[i].otherprob)
        if nodedict[i].chance:
            print(i)
            print("Chance")
            print(nodedict[i].probs)
        if nodedict[i].leaf:
            print(i)
            print("Leaf")
            print(nodedict[i].val)
        print()

def parse_and_check(fname):
    nodedict = {}
    try:
        nodedict = parse(fname)
    except:
        print("\nError: graph file not a txt file or a different error, listed above, occurred\n")
        exit(1)
    return nodedict