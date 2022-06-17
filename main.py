from bb_tools import *
import os

os.chdir("./data")
nb_var, nb_constr, fo, constr = read_instance("p1.txt")
sol = execute(nb_var, nb_constr, fo, constr)
print(sol)


nb_var, nb_constr, fo, constr = read_instance("p2.txt")
sol = execute(nb_var, nb_constr, fo, constr)
print(sol)
