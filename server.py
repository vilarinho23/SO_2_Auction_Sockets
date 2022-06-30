#Importar librarias adicionais
import os
import socket
import threading
import time

#Constantes
FORMAT = "'utf-8'"
BUFF = 4096 

#Defenir ip e porta do servidor
host = '127.0.0.1'
port = 12345

#Criar um socket para o servidor e coloca-lo à procura de conexões
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#Variaveis e listas
clientes = []
nomes = []
nome_obj = ''
preço_obj = ''
nome_comp = ''
licitaçoes = False
numero_lici = 0
estado_leilao = False
clientes_conectados = 0
#Enviar mensagem para todos os clientes ativos
def transmitir(mensagem):
    for cliente in clientes:
        cliente.send(mensagem)

#Lidar com as mensagens dos diversos clientes e caso o mesmo de desconecte, remover da lista de clientes
def lidar(cliente):
    global clientes_conectados
    while True:
        try:
            mensagem = cliente.recv(BUFF).decode(FORMAT)
            if estado_leilao == True:
                licitações(cliente, mensagem)
            if estado_leilao == False:
                cliente.send("Nenhum leilão a decorrer".encode(FORMAT))
        except:
            index = clientes.index(cliente)
            nome_utilizador = nomes[index]
            clientes.remove(cliente)
            nomes.remove(nome_utilizador)
            clientes_conectados -= 1
            cliente.close()
            transmitir(f"{nome_utilizador} saiu da casa de leilões!".encode(FORMAT))
            break

#Receber diversos clientes e criar uma thread da função lidar para cada um
def receber():
    global clientes_conectados
    while clientes_conectados < 20:
        cliente, address = server.accept()
        
        nome_utilizador = cliente.recv(BUFF).decode(FORMAT)
        nomes.append(nome_utilizador)
        clientes.append(cliente)
        clientes_conectados += 1
        if estado_leilao == True:
            cliente.send(f"Leilão de {nome_obj} ativo. Preço Atual: {preço_obj}€".encode(FORMAT))
        thread = threading.Thread(target=lidar, args=(cliente,))
        thread.start()
    
#Receber as licitações por parte dos clientes e validar as mesmas
def licitações(cliente, mensagem):
    index = clientes.index(cliente)
    nome_utilizador = nomes[index]
    global preço_obj
    global nome_comp
    global licitaçoes
    global numero_lici
    try:
        int(mensagem)
        if nome_comp == nome_utilizador:
            cliente.send(f"Não pode licitar duas vezes seguidas".encode(FORMAT))
        else:
            if int(mensagem) < preço_obj:
                cliente.send(f"Licitação baixa demais".encode(FORMAT))
            elif int(mensagem) == preço_obj:
                if not nome_comp:
                    preço_obj = int(mensagem)
                    nome_comp = nome_utilizador
                    licitaçoes = True
                    numero_lici = 1
                    transmitir(f"{nome_utilizador} licitou {mensagem}€".encode(FORMAT))
                else:
                    cliente.send(f"Licitação baixa demais".encode(FORMAT))
            else:
                preço_obj = int(mensagem)
                nome_comp = nome_utilizador
                licitaçoes = True
                numero_lici = 1
                transmitir(f"{nome_utilizador} licitou {mensagem}€".encode(FORMAT))
                #print(f'{nome_utilizador} licitou {mensagem}€')
    except:
        cliente.send("Input Inválido.".encode(FORMAT))

#Menu do servidor
def menu():
    while(True):
        printdomenu()
        op = ''
        try:
            op = int(input("Escolha a operação desejada: "))
        except:
            print("ERRO. Insira um número...")
        if op == 1:
            op1()
        elif op == 2:
            op2()
        elif op == 3:
            op3()
        elif op == 4:
            print("Obrigado e volte sempre.")
            time.sleep(5)
            os._exit(0)
        else:
            print("Opção inválida. Insira um número entre 1 e 4.")

#Dar print das opções do menu
def printdomenu():
    print ("1 -- Criar Leilão" )
    print ("2 -- Lista de Clientes" )
    print ("3 -- Objetos Leiloados" )
    print ("4 -- Sair" )

#Opção de criar leilão
def op1():
    global estado_leilao
    global nome_obj
    global preço_obj
    global nome_comp
    nome_obj = input("Escolha o nome do objeto que deseja leiloar: ")
    while True:
        try:
            preço_obj = int(input("Escolha o preço base: "))
        except:
            print("ERRO. Insira um número...")
        else:
            break
    transmitir(f"Leilão de {nome_obj} ativo. Preço Base: {preço_obj}€".encode(FORMAT))
    estado_leilao = True
    nome_comp = ''
    while True:
        if licitaçoes == True:
            temp()
            if estado_leilao == True:
                continue
            else:
                break
        else:
            continue
    f = open("leiloes.txt","a")
    f.write(f"Objeto Leiloado: {nome_obj}  Preço: {preço_obj}€  Comprador: {nome_comp}\n")
    f.close()

#Temporizador para se nao houver licitações, acabar o leilão
def temp():
    global numero_lici
    global estado_leilao
    if numero_lici > 0:
        numero_lici = 0
        time.sleep(5)
        if numero_lici == 0:
            time.sleep(10)
            if numero_lici == 0:
                transmitir("E vai um...".encode(FORMAT))
                #print("E vai um...")
                time.sleep(3)
                if numero_lici == 0:
                    transmitir("E vai dois...".encode(FORMAT))
                    #print("E vai dois...")
                    time.sleep(3)
                    if numero_lici == 0:
                        transmitir("E vai três...".encode(FORMAT))
                        #print("E vai três..")
                        transmitir(f"Leilão de {nome_obj} concluido. Preço Final: {preço_obj}€. Comprador: {nome_comp}".encode(FORMAT))
                        print(f"Leilão de {nome_obj} concluido. Preço Final: {preço_obj}€. Comprador: {nome_comp}")
                        estado_leilao = False

#Opção de listar no servidor todos os clientes ativos no leilao
def op2():
    if nomes:
        print("")
        print("Lista de Clientes Ativos")
        print("------------------------")
        for nome in nomes:
            print(nome)
        print("------------------------")
        print("")
    else:
        print("")
        print("Não existem clientes ativos")
        print("")

#Opção de mostrar todos os leilões registados no ficheiro leilao.txt que os contem
def op3():
    f_tam = os.path.getsize("leiloes.txt")
    if f_tam == 0:
        print("")
        print("Não existem objetos leiloados")
        print("")
    else:
        count = 0
        f = open("leiloes.txt","r")
        linhas = f.readlines()
        for i in linhas:
            count += 1
            if count == 1:
                print("")
                print(i)
            if count > 1:
                print(i)
        f.close()

#Iniciar thread para receber clientes e iniciar o menu no servidor
receber_thread = threading.Thread(target=receber)
receber_thread.start()
menu()


