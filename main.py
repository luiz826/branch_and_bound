from cv2 import solve
from bb_tools import *
import os

os.chdir("./data")
nb_var, nb_constr, fo, constr = read_instance("p1.txt")

op = [0]*nb_var

model = create_model_LP(nb_var, nb_constr, fo, constr, op)

no = solve_LP(model)

print(no)
