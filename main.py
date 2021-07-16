from parse import parse_and_check
import ideal_policy as ip


def start(fname,tolerance,iterations,maximize,df):
    print()
    ip.ideal_policy(parse_and_check(fname),tolerance,iterations,maximize,df)