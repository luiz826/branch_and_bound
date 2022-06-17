'''
    Algoritmo Branch and Bound

    Caio Lucas da Silva Chacon - 20200025769
    Luiz Fernando Costa dos Santos - 20200025446 
'''
from bb_tools import *
from sys import argv

nb_var, nb_constr, fo, constr = read_instance("./data/"+argv[1])
sol = execute(nb_var, nb_constr, fo, constr, False)
print(sol)
