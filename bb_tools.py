'''
    Algoritmo Branch and Bound
    
    Caio Lucas da Silva Chacon - 20200025769
    Luiz Fernando Costa dos Santos - 20200025446 
'''
from mip import (Model, 
                MAXIMIZE, 
                CONTINUOUS,
                CBC,
                xsum)
from math import ceil, floor

is_int = lambda x : x//1 == x # Função para definir se o numero é inteiro (True) ou fracionário (False)
dis_0_5 = lambda x: abs(x - 0.5) # Função para definir qual a distancia de um numero para 0.5 

class Node:
    '''
        Classe que serve para armazenar as variaveis x, a solução z, as restrições e as operações
    '''
    def __init__(self, x: list, z: float, constr: list, op: list):
        self.x = x
        self.z = z
        self.constr = constr
        self.op = op

    def __repr__(self) -> str: 
        return "\nx = " + str(self.x) + "\nz = " + str(self.z)

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


def create_and_solve_model_LP(nb_var: int, nb_constr: int, fo: list, constr: list, op) -> Node:
    """
        Serve para criar um modelo no MIP mais facilmente

        op = é uma lista para cada restrição que vai dizer 
            qual o operador sera utilizado na restrição:
                0 se <=
                1 se >= 
                2 se ==

        p = é o contador do nó
    """ 
    model = Model(sense=MAXIMIZE, solver_name=CBC)

    x = [model.add_var( var_type=CONTINUOUS, lb=0.0, ub=1.0,
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
    _ = model.optimize()
    x = [v.x for v in model.vars]
    z = model.objective_value

    no = Node(x, z, constr, op)

    return no

def choose_to_cut(x) -> int:
    '''
        Recebe as variaveis x e escolhe qual deve ser a escolhida para fazer a ramificação
    '''
    distances = list(map(dis_0_5, x)) # Distancia de cada variavel para 0.5

    m = float("inf")
    argmin = 0
    for i in range(len(distances)):
        if (not is_int(x[i])) and (distances[i] < m): 
        # se a variavel for inteira AND 
        # se ela tiver uma distancia menor que a menor distancia 
            m = distances[i]
            argmin = i
            
    return argmin

def cut(var) -> tuple:
    '''
        dado a variavel que vai ramificar, essa função ramifica (transoforma 0.6 em 1 e 0, por exemplo)
    '''
    return ceil(var), floor(var)

def create_constr(no: Node, nb_var: int, var: int, lim: int, op: int) -> tuple:
    '''
        Serve para criar uma nova restrição para o modelo
        dado a variavel de ramifiação, o valor floor e ceil dela e o numero de variaveis
    '''

    cons = [] # restrição 
    for i in range(nb_var):
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

def execute(nb_var: int, nb_constr: int, fo: list, constr: list, verbose=True):
    '''
        Roda o branch and bound
    '''
    # Criando o primeiro modelo
    op = [0]*nb_constr
    no = create_and_solve_model_LP(nb_var, nb_constr, fo, constr, op)

    lower_bound = float("-inf")

    q = [] # Estrutura de dados Fila (queue por isso o nome q)
    q.append(no)

    solution = None
    solution_z = 0

    while len(q) > 0:
        i = q[0] 
    
        if i.x == [None]*nb_var:# Poda por inviabilidade
            poda = "Poda por inviabilidade"
            q.pop(0)
    
        elif all(list(map(is_int,i.x))): # Poda por integralidade
            if i.z > lower_bound:
                lower_bound = i.z
            poda = "Poda por integralidade"
            q.pop(0)
            if i.z > solution_z:
                solution_z = i.z
                solution = i
        
        elif i.z < lower_bound: # Poda por limitante
            poda = "Poda por limitante"
            q.pop(0)
        
        else: # Quando as variaveis não são inteiras
            poda = ""
            var = choose_to_cut(i.x)
            up, down = cut(i.x[var])

            for j, num in enumerate([down, up]):
                constr, op = create_constr(i,nb_var, var, num, j)      
                new_no = create_and_solve_model_LP(nb_var, nb_constr, fo, constr, op)    
                q.append(new_no)

            nb_constr = len(constr)
            q.pop(0)
        
        if verbose:
            print("-"*100)
            print(f"\nNo da iteração atual: {i}") 
            print(poda)        
        
    if solution_z == 0:
        print("\nNão existe solução ótima inteira!")
        return None

    print("-"*100)
    print("\nSolução ótima encontrada!")
    
    return solution
