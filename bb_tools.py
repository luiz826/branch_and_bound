from mip import (Model, 
                MAXIMIZE, 
                BINARY,
                CBC,
                xsum)

class Node:
    def __init__(self, x: list, z: float, status):
        self.x = x
        self.z = z
        self.status = status

    def __repr__(self) -> str:
        return "Status = " + str(self.status) + "\nx = " + str(self.x) + "\nz = " + str(self.z)

def create_model_LP(nb_var: int, nb_constr: int, fo: list, constr: list, op) -> tuple:
    """
        op = é uma lista para cada restrição que vai dizer 
            qual o operador sera utilizado na restrição:
                0 se <=
                1 se >= 
                2 se ==
    """
    model = Model(sense=MAXIMIZE, solver_name=CBC)

    x = [model.add_var( var_type=BINARY, 
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

def choose_variable_to_branch(node:Node) -> int: #indice
    pass

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
