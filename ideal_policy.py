import random
import numpy as np
import copy


def random_policy(nodedict):
    policy = {}
    keys = nodedict.keys()
    decisions = {}
    for i in keys:
        iNode = nodedict[i]
        if iNode.decision or iNode.chance:
            decisions[i] = nodedict[i]
            if iNode.decision:
                policy[i] = random.choice(iNode.children) # might need outter nodedict index
    return policy,decisions

def get_prob(nodedict,i,j,policy):
    iNode = nodedict[i]
    if iNode.chance:
        ichildren = iNode.children
        for k in np.arange(len(ichildren)):
            if ichildren[k] == j:
                return iNode.probs[k]
    # print(policy)
    # decision node
    if policy[i] == j:
        return iNode.probs
    return iNode.otherprob

def initialize(nodedict):
    equations = np.zeros((len(nodedict),len(nodedict) + 1)) # extra column is for augmented 0 column where our valuation will be after RREF
    keys = nodedict.keys()
    # for i in keys:
    #     iindex = indices[i]
    #     equations
    #     # if nodedict[i].decision or nodedict[i].chance:
    #     #     equations[iindex,iindex] = -1
    #     # else:
    #     #     equations[iindex,iindex] = 1
    np.fill_diagonal(equations,-1)
    return equations

def valuation(nodedict,policy,df,indices,equations):
    keys = nodedict.keys()
    for i in keys:
        iindex = indices[i]
        iNode = nodedict[i]
        ichildren = iNode.children
        for j in ichildren:
            if iNode.decision or iNode.chance:
                jNode = nodedict[j]
                if jNode.decision or jNode.chance:
                    equations[iindex,indices[j]] += df * get_prob(nodedict,i,j,policy)
                else:
                    equations[iindex,-1] -= df * jNode.val * get_prob(nodedict,i,j,policy)
        if iNode.leaf:
            equations[iindex,-1] -= iNode.val
    # print(equations)
    try:
        return np.linalg.solve(equations[:,:-1],equations[:,-1])
    except: # singular matrix translates to infinite like payoff
        return valuation(nodedict,random_policy(nodedict),df,indices,equations)
    
def get_expectation(i,j,nodedict,expectations,df,indices):
    expectation = 0
    iNode = nodedict[i]
    otherprob = iNode.otherprob
    ichildren = iNode.children
    jNode = nodedict[j]
    for c in ichildren:
        if jNode.decision or jNode.chance:
            if c == j:
                expectation += df * iNode.probs * expectations[indices[j]]
                if j == i:
                    expectation += df * iNode.otherprob * expectations[indices[j]]
            else:
                expectation += df * otherprob * expectations[indices[c]]
        else:
            if c == j:
                expectation += df * iNode.probs * jNode.val
            else:
                expectation += df * otherprob * jNode.val
    if iNode.leaf:
        expectation += iNode.val
    return expectation

def get_extreme(maximize):
    if maximize:
        return -10e9
    return 10e9

def update(extreme,expectation,maximize):
    if maximize:
        if extreme < expectation:
            return expectation,True
        return extreme,False
    if extreme > expectation:
        return expectation,True
    return extreme,False

def improve(policy,decisions,df,maximize,expectations,indices,nodedict):
    new_expectations = copy.deepcopy(expectations)
    keys = decisions.keys()
    max_diff = 0
    for i in keys:
        if nodedict[i].decision:
            extreme = expectations[indices[i]]
            ichildren = decisions[i].children
            iindex = indices[i]
            for j in ichildren:
                if j != policy[i]:
                    expectation = get_expectation(i,j,nodedict,expectations,df,indices)
                    extreme,update_e = update(extreme,expectation,maximize)
                    if update_e:
                        policy[i] = j
                        new_expectations[iindex] = extreme
            max_diff = max(max_diff,abs(expectations[iindex] - new_expectations[iindex]))
    return policy,max_diff,new_expectations

def simulate_improve(nodedict,policy,maximize,df,decisions,indices,equations):
    return improve(policy,decisions,df,maximize,valuation(nodedict,policy,df,indices,equations),indices,nodedict)

def print_policy(policy,expectations,indices,nodedict):
    keys = policy.keys()
    for i in keys:
        iNode = nodedict[i]
        if iNode.decision and len(iNode.children) > 1:
            print(i + "->" + policy[i])
    print()
    keys = nodedict.keys()
    for i in keys:
        iNode = nodedict[i]
        if iNode.chance or iNode.decision:
            print(i + "=" + str(expectations[indices[i]]),end=" ")
        else:
            print(i + "=" + str(iNode.val),end=" ")
    print("\n")

def index(nodedict,decisions):
    indices = {}
    keys = decisions.keys()
    j = 0
    for i in keys:
        indices[i] = j
        j += 1
    keys = nodedict.keys()
    for i in keys:
        try:
            a = indices[i]
        except KeyError:
            indices[i] = j
            j += 1
    return indices

def check_policy_exists(nodedict,policy,df,indices,equations):
    if len(policy) == 0: # all chance nodes
        print("No policy for all chance node MDP")
        print_policy(policy,valuation(nodedict,policy,df,indices,equations),indices,nodedict)
        exit(1)

def get_situated(nodedict,df):
    policy,decisions = random_policy(nodedict)
    indices = index(nodedict,decisions)
    equations = initialize(nodedict)
    check_policy_exists(nodedict,policy,df,indices,equations)
    return policy,decisions,indices,equations

def ideal_policy(nodedict,tolerance,iterations,maximize,df):
    policy,decisions,indices,equations = get_situated(nodedict,df)
    max_diff = 10e9
    i = 0
    # print(indices)
    while max_diff > tolerance and i < iterations:
        policy,max_diff,expectations = simulate_improve(nodedict,policy,maximize,df,decisions,indices,equations)
        equations = initialize(nodedict)
        i += 1
    print_policy(policy,expectations,indices,nodedict)