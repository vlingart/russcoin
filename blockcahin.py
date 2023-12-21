#!/usr/bin/env python
# coding: utf-8

# In[1]:


from datetime import datetime
from hashlib import sha256
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
import random
import json


# In[2]:


class MerkleTree:
    def __init__(self, values)-> None:
        self.__buildTree(values)

    def __buildTree(self, values)-> None:
        leaves: List[Node] = [Node(None, None, Node.doubleHash(e)) for e in values]
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1:][0])
        self.root: Node = self.__buildTreeRec(leaves)

    def __buildTreeRec(self, nodes):
        half: int = len(nodes) // 2

        if len(nodes) == 2:
            return Node(nodes[0], nodes[1], Node.doubleHash(nodes[0].value + nodes[1].value))

        left: Node = self.__buildTreeRec(nodes[:half])
        right: Node = self.__buildTreeRec(nodes[half:])
        value: str = Node.doubleHash(left.value + right.value)
        return Node(left, right, value)

    def printTree(self)-> None:
        self.__printTreeRec(self.root)

    def __printTreeRec(self, node)-> None:
        if node != None:
            print(node.value)
            self.__printTreeRec(node.left)
            self.__printTreeRec(node.right)

    def getRootHash(self)-> str:
        return self.root.value


# In[3]:


def H(bytes_string_to_hash):
    return sha256(bytes_string_to_hash).digest()


# In[4]:


def sign(bytes_to_sign,sk,n):
    return pow(int.from_bytes(bytes_to_sign, "big"),sk,n)


# In[5]:


D=2
coinbase=1000000


# In[6]:


bytes(b'0'*30)


# In[7]:


class Blockchain():
    global coinbase
    def __init__(self,Clients,Nodes):
        global coinbase
        self.Nodes=Nodes
        self.Clients=Clients
    
        #генерация генезисного блока
    
        self.genesis_Block=Block()
        print('Генезис блок сформирован:\n',self.genesis_Block.header,'\n\n\n\n')
        self.miner_node=random.choice(Nodes)
        self.miner_client=random.choice(Clients)
        self.genesis_Block.Finalize(self.miner_client)
        
        #рассылка блока по нодам и проверка
        
        for node in Nodes:
            if not node.gen_validation(self.genesis_Block):
                print('Ошибка валидации генезис блока')
            
            #если проверка на нодах прошла успешно, до блок добавляется в их реплику цепочки
            node.blocks.append(self.genesis_Block)
            
            #Удаление старых output_UTXO и добавление новых.
            for trans in self.genesis_Block.body['tr']:
                for iUTXO in trans['i_UTXO']:
                    #проверка наличия output_UTXO на попытку использовать несуществующих UTXO
                    try:
                        node.UTXO.remove(iUTXO)
                    except:
                        print('Попытка двойного использования актива!')
                for oUTXO in trans['o_UTXO']:
                    node.UTXO.append(oUTXO.copy())
                
        #добавление майнеру награды
        self.miner_client.UTXO.append({'addr':self.miner_client.addr,'value':5})
        print(f'Награда 5 рускойнов добавлена майнеру {self.miner_client.name}\n\n')
        
        print('Генезис блок добавлен в цепочку:\n',self.genesis_Block.header, self.genesis_Block.body)
        coinbase=coinbase-5
        
        
        
    def step(self):
        global coinbase
        
        #случайный выбор майнера-ноды и майнера-клиента
        self.miner_client=random.choice(self.Clients)
        self.miner_node=random.choice(self.Nodes)
    
        #генерация нового блока
        self.current_Block=self.miner_node.Block_creation()
       
    
        #пользовательски интерфейс
        user_command='start'
        while user_command != '0':
            for client in self.Clients:
                print(client.name)
            client_number=int(input('Выберете клиента:\n\n'))
            UTXOs=self.Clients[client_number].balance_show(self.miner_node)
            print(self.Clients[client_number].balance_show(self.miner_node))
            i_UTXO=UTXOs[int(input('Выберете UTXO:\n\n'))]
            addreses=[]
            for Cl in self.Clients:
                print(Cl.addr)
                addreses.append(Cl.addr)
            addres=addreses[int(input('Выберете адрес получателя:\n\n'))]
            val=int(input('Введите сумму перевода:\n\n'))
            print(i_UTXO)
            new_trans=self.Clients[client_number].transaction_creation(addres, val, i_UTXO)
            print(new_trans,'\n\n')
            self.miner_node.transfer(new_trans)
            print(self.current_Block.header, self.current_Block.body)
            user_command=input('Продолжить?\n\n')
        
        
        
        
        
        
        print('Новый блок сформирован:\n',self.current_Block.header,'\n\n\n\n')

        self.current_Block.Finalize(self.miner_client)
        
        #рассылка блока по нодам и проверка
        
        for node in self.Nodes:
            if not node.validation(self.current_Block):
                print('Ошибка валидации блока')
                return 0
            #если проверка на нодах прошла успешно, до блок добавляется в их реплику цепочки
            node.blocks.append(self.current_Block)
            
            #Удаление старых output_UTXO и добавление новых.
            for trans in self.current_Block.body['tr']:
                for iUTXO in trans['i_UTXO']: 
                    #проверка наличия output_UTXO на попытку использовать несуществующих UTXO
                    try:
                        #print(node.UTXO)
                        #print(iUTXO)
                        node.UTXO.remove(iUTXO)
                    except:
                        #print(node.UTXO)
                        #print(iUTXO)
                        print('Попытка двойного использования актива!')
                        return 0
                for oUTXO in trans['o_UTXO']:
                    node.UTXO.append(oUTXO.copy())
                
        #добавление майнеру награды
        self.miner_client.UTXO.append({'addr':self.miner_client.addr,'value':5})
        print(f'Награда 5 рускойнов добавлена майнеру {self.miner_client.name}\n\n')
        coinbase=coinbase-5
        print('Новый блок добавлен в цепочку:\n',self.current_Block.header, self.current_Block.body)
        coinbase=coinbase-5


# In[8]:


class Block():
    global coinbase
    
    #создание нового блока
    def __init__(self, heigh=0, time= datetime.now().strftime("%d/%m/%Y %H:%M:%S"), root='', prev=b'0'*256, transactions=[{'i_UTXO':[{'addr':'coinbase','value':0}],'o_UTXO':[{'addr':'miner_addr','value':5},{'addr':'coinbase','value':0}]}]):
        global coinbase
        trans=transactions.copy()
        self.heigh=heigh
        self.time=time
        self.root=root
        self.prev=prev
        trans[0]['o_UTXO'][1]['value']=coinbase-5
        trans[0]['i_UTXO'][0]['value']=coinbase
        self.header={'heigh':heigh, 'time': time, 'root':root, 'prev': prev}
        self.body={'coinbase':coinbase, 'tr':trans.copy()}
    
    #финализация блока. процесс майнинга
    def Finalize(self,miner):
        nonce,hsh=miner.mine(self.header)
        self.nonce=nonce
        self.hash=hsh
        self.header['nonce']=nonce
        self.header['hash']=hsh
        self.body['tr'][0]['o_UTXO'][0]['addr']=miner.addr


# In[9]:


class Node():
    global coinbase
    
    #добавление ноды
    def __init__(self):
        global coinbase
        self.UTXO=[{'addr':'coinbase','value':coinbase}]
        self.blocks=[]
    def Block_creation(self):
        self.new_block=Block(heigh=self.blocks[-1].heigh+1, prev=self.blocks[-1].hash)
        return(self.new_block)
    
    #проверка блока на все условия
    def validation(self,block):
        global coinbase
        header_hash=H((str(block.header['heigh'])+block.header['time']+block.header['root']+block.header['prev'].hex()+block.header['nonce'].hex()).encode()) #bytes
        bin_header_hash=bin(int(header_hash.hex(), base=16))[2:]
        
        if (bin_header_hash [-2:] != '0'*D):
            print ('Nonce is incorrect!')
            return 0
        print ('Successfull Nonce check!')
        
        if (block.header['heigh']-1!=self.blocks[-1].header['heigh']):
            print ('Block order is incorrect!')
            return 0
        print ('Successfull Block order check!')
        
        if (block.header['prev']!=self.blocks[-1].header['hash']):
            print ('Blocks previous hash is incorrect!')
            return 0
        print ('Successfull previous hash check!')
            
        if (block.header['time']>self.blocks[-1].header['time']):
            print ('Blocks time is incorrect!')
            return 0
        print ('Successfull Blocks time check!')
        
        if (block.body['coinbase']+5!=self.blocks[-1].body['coinbase']):
            print ('Blocks coinbase is incorrect!')
            return 0
        print ('Successfull coinbase check!')
        
        for trans in block.body['tr']:
            transaction_bytes=json.dumps(trans, indent=2).encode('utf-8')
            try:
                if (sign(transaction_bytes,trans['рk'],self.n))!=trans['sign'] and False:
                    print ('Wrong signature!')
                    return 0
            except:
                print ('Successfull signatures check!')
        
        try:
            if(MerkleTree(transaction)!=root):
                print('Incorrect Merklee Tree root!')
        except:
               print ('Successfull Merklee Tree root check!\n\n')
        return 1
    
    #проверка генезис-блока на все условия
    def gen_validation(self,block):
        header_hash=H((str(block.header['heigh'])+block.header['time']+block.header['root']+block.header['prev'].hex()+block.header['nonce'].hex()).encode()) #bytes
        bin_header_hash=bin(int(header_hash.hex(), base=16))[2:]
        if (bin_header_hash [-2:] != '0'*D):
            print('Nonce is incorrect!')
            return 0
        return 1
    
    #нода проверяет возможность транзакции и добавляет её в новый блок
    def transfer(self, transaction):
        if(transaction['i_UTXO'][0]['value']-transaction['o_UTXO'][0]['value']>=0):
            if(transaction['i_UTXO'][0]['value']==transaction['o_UTXO'][0]['value']+transaction['o_UTXO'][1]['value']):
                self.new_block.body['tr'].append(transaction)
                return 1
        print('Транзакция невозможна, недостаточно средств!')
        return 0


# In[10]:


class Client():
    global coinbase
    
    #создание клиента, генерация ключей для него и генерация адреса из ключей
    def __init__(self,name='a'):
        self.name=random.choice(['vaya','petya','boris','semen','gayorgiy', 'sergay', 'ivanya'])
        key=RSA.generate(1024)
        self.pk=key.e
        self.sk=key.d
        self.n=key.n
        self.addr=H(self.sk.to_bytes(256, 'big')).hex()
        self.UTXO=[]
        
        
    #функция майнинга
    def mine(self, block_header):
        nonce=get_random_bytes(32)
        header_hash=H((str(block_header['heigh'])+block_header['time']+block_header['root']+block_header['prev'].hex()+nonce.hex()).encode()) #bytes
        bin_header_hash=bin(int(header_hash.hex(), base=16))[2:]
        while bin_header_hash [-2:] != '0'*D:
            nonce=get_random_bytes(32)
            header_hash=H((str(block_header['heigh'])+block_header['time']+block_header['root']+block_header['prev'].hex()+nonce.hex()).encode()) #bytes
            bin_header_hash=bin(int(header_hash.hex(), base=16))[2:]
        return(nonce,header_hash)
    
    #создание транзакции клиентом
    def transaction_creation(self, addr, ammount, i_UTXO):
        transaction={'i_UTXO':[i_UTXO], 'o_UTXO':[{'addr':addr, 'value':ammount},{'addr':self.addr,'value':i_UTXO['value']-ammount}]}
        transaction_bytes=json.dumps(transaction, indent=2).encode('utf-8')
        transaction_signature=sign(transaction_bytes,self.sk,self.n)
        transaction['sign']=transaction_signature
        transaction['pk']=self.pk
        transaction['n']=self.n
        return(transaction)
    
    
    def balance_show(self,Node):
        balance=[]
        for trans in Node.UTXO:
            if trans['addr']==self.addr:
                balance.append(trans)
        return(balance)


# In[11]:


coinbase


# In[12]:


C1=Client()
C2=Client()
C3=Client()
print(C1.name,C1.addr)
print(C2.name,C2.addr)
print(C3.name,C3.addr)


# In[13]:


N1=Node()
N2=Node()
N3=Node()


# In[14]:


bc=Blockchain([C1,C2,C3],[N1,N2,N3])


# In[15]:


bc.step()


# In[16]:


bc.step()


# In[ ]:


bc.step()


# In[18]:


N1.blocks[1].body


# In[19]:


N1.UTXO


# In[20]:


bc.current_Block.body


# In[21]:


C3.balance_show(N1)

