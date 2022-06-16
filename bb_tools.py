'''
Alguns problemas:

- ainda falta incluir o upper e lower bound na parada, ou seja, a poda por limitante
'''
from xml.dom import NO_DATA_ALLOWED_ERR
from mip import (Model, 
                MAXIMIZE, 
                CONTINUOUS,
                CBC,
                xsum)
from math import ceil, floor
import sys 


is_int = lambda x : x//1 == x # Função para definir se o numero é inteiro ou não (fracionário)
dis_0_5 = lambda x: abs(x - 0.5) # Função para definir qual a distancia do numero para 0.5 (o professor pede issp)

class Node:
    '''
        Classe que serve para armazenar as variaveis x e z, alem do status que vem do MIP
    '''
    def __init__(self, x: list, z: float, status, constr, op, nb_var):
        self.x = x
        self.z = z
        self.status = status
        self.constr = constr
        self.op = op
        self.nb_var = nb_var

    def __repr__(self) -> str: # esse método serve so pra printar bonitinho
        return "Status = " + str(self.status) + "\nx = " + str(self.x) + "\nz = " + str(self.z)

def read_instance(filePath: str) -> tuple:
    '''
        lê o arquivo
    '''
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


def create_and_solve_model_LP(nb_var: int, nb_constr: int, fo: list, constr: list, op) -> tuple:
    """
        Serve para criar um modelo no MIP mais facilmente

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

    model.verbose = 0
    status = model.optimize()
    
    x = [v.x for v in model.vars]
    z = model.objective_value

    no = Node(x, z, status, constr, op, nb_var)

    return no

def choose_to_cut(x) -> int:
    '''
        Recebe as variaveis x e escolhe qual deve ser a escolhida para fazer a ramificação
    '''
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
    '''
        dado a variavel que vai ramificar, essa função ramifica (transoforma 0.6 em 1 e 0, por exemplo)
    '''
    return ceil(var), floor(var)

def create_constr(no, var, lim, op):
    '''
        Serve para criar uma nova restrição para o modelo
        dado a variavel de ramifiação, o valor floor e ceil dela e o numero de variaveis
    '''

    cons = [] # restrição 
    for i in range(no.nb_var):
        if i == var:
            cons.append(1)
        else:
            cons.append(0)
        
    cons.append(lim)

    new_constr = no.constr[:]
    new_constr.append(cons)

    new_op = no.op[:]
    new_op.append(op)
    return new_constr, new_op

def execute(nb_var, nb_constr, fo, constr):
    '''
        Roda o branch and bound
    '''
    ### Criando o primeiro modelo, o P0
    op = [0]*nb_constr
    no = create_and_solve_model_LP(nb_var, nb_constr, fo, constr, op)

    # só criei essas variaveis, mas ainda precisamos ver como encaixar elas
    upper_bound = float("inf")
    lower_bound = float("-inf")

    q = [] #FILA 
    q.append(no)

    # Aqui tu roda o código e ve no terminal que fica mais facil de entender
    while len(q) != 0:
        i = q[0] 
        
        print("-"*150)
        print(f"NOVA ITER - No da vez = {i.x}")
        print("-"*150)
        print("TAMANHO DA FILA: ", len(q)) # tamanho da fila     
        if i.x == [None]*nb_var:# Poda por inviabilidade
            print("INFEASIBLEEEEEEEEEEEEEEEEEEe") 
            q.pop(0)
            continue
        
        if all(list(map(is_int,i.x))): # se todas as variaveis forem inteiras
            lower_bound = i.z 
            print("INTREGRALIDADEEEEEEEEEEEEEEEe")
            q.pop(0)
            continue
        else:
            var = choose_to_cut(i.x)
            up, down = cut(i.x[var])
            upper_bound = i.z
            print("variavel escolhida ", var)

            constr_l, op_l = create_constr(i, var, down, 0)  
            constr_r, op_r = create_constr(i, var, up, 1)  

            nb_constr = len(constr_l)
            no_left = create_and_solve_model_LP(nb_var, nb_constr, fo, constr_l, op_l)

            print("\nNÓ ESQUERNO")
            #print("\nENTRADA: ", nb_var, nb_constr, fo, constr_l, op_l, "\n")
            print("\nRESULTADO: ",no_left.x, no_left.z)

            nb_constr = len(constr_r)
            no_right = create_and_solve_model_LP(nb_var, nb_constr, fo, constr_r, op_r)
    
            print("\nNÓ DIREITO")
            #print("\nENTRADA: ", nb_var, nb_constr, fo, constr_r, op_r, "\n")
            print("\nRESULTADO: ", no_right.x, no_right.z)
            

            q.append(no_left)
            q.append(no_right)
            
            q.pop(0)


    print("ACABOU")
