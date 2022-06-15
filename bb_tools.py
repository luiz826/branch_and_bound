from mip import (Model, 
                MAXIMIZE, 
                CONTINUOUS,
                CBC,
                xsum)
from math import ceil, floor
import sys 

is_int = lambda x : x//1 == x
dis_0_5 = lambda x: abs(x - 0.5)

class Node:
    def __init__(self, x: list, z: float, status):
        self.x = x
        self.z = z
        self.status = status
        self.poda = False # devo podar

    def __repr__(self) -> str:
        return "Status = " + str(self.status) + "\nx = " + str(self.x) + "\nz = " + str(self.z)

    def set_poda(self, val:bool):
        self.poda = val

def create_model_LP(nb_var: int, nb_constr: int, fo: list, constr: list, op) -> tuple:
    """
        op = é uma lista para cada restrição que vai dizer 
            qual o operador sera utilizado na restrição:
                0 se <=
                1 se >= 
                2 se ==
    """
    model = Model(sense=MAXIMIZE, solver_name=CBC)

    x = [model.add_var( var_type=CONTINUOUS, lb=0.0,
                        name="x_"+str(i))
                        for i in range(nb_var)]

    model.objective = xsum(fo[i]*x[i] for i in range(nb_var))

    for c in range(nb_constr):
        if op[c] == 0:
            model += xsum(x[i]*constr[c][i] for i in range(nb_var)) <= constr[c][-1]
        elif op[c] == 1:
            model += xsum(x[i]*constr[c][i] for i in range(nb_var)) >= constr[c][-1]
        else: #op[c] == 2
            model += xsum(x[i]*constr[c][i] for i in range(nb_var)) == constr[c][-1]

    return model

def solve_LP(model:Model) -> Node: 
    status = model.optimize()
    
    x = [v.x for v in model.vars]
    z = model.objective_value

    no = Node(x, z, status)

    return no

def read_instance(filePath: str) -> tuple:
    f = open(filePath, "r")

    l = f.readline()
    nb_var, nb_constr = int(l.split()[0]), int(l.split()[1])
    
    l = f.readline()
    fo = [float(c) for c in l.split()]
    
    constr = []
    for _ in range(nb_constr):
        l = f.readline()
        constr.append([float(c) for c in l.split()])

    f.close()

    return nb_var, nb_constr, fo, constr

def choose_to_cut(x) -> int:
    minimuns = list(map(dis_0_5, x))
    m = sys.maxsize
    argmin = 0
    for i in range(len(minimuns)):
        if is_int(x[i]):
            continue
        if minimuns[i] < m:
            m = minimuns[i]
            argmin = i
            
    return argmin

def cut(var) -> tuple:
    return ceil(var), floor(var)

def execute(nb_var, nb_constr, fo, constr):

    op = [0]*nb_constr
    model = create_model_LP(nb_var, nb_constr, fo, constr, op)
    no = solve_LP(model)

    q = []
    q.append(no)
    for i in q:
        if all(list(map(is_int,i.x))):
            i.set_poda(True)
        else:
            var = choose_to_cut(i.x)
            up, down = cut(i.x[var])
            print(down, up)

        if i.poda:
            q.pop(0)
        else:
            #q.append()
            pass
