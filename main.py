from bb_tools import *
import os
import sys 

os.chdir("./data")
nb_var, nb_constr, fo, constr = read_instance("p1.txt")
#print(nb_var, nb_constr, fo, constr)
execute(nb_var, nb_constr, fo, constr)

# ver como tira o print do python mip