from microbit import *
import radio
radio.on()
incomming

initialize = "micro_req;1"          # Message signifiant qu'un Microbit veut démarrer la communication
accept = "micro_acc"                # Message signifiant que le Microbit accepte la communication (permet de valider le passage à la nouvelle adresse de communication)
default_address = "0x90548090"      # adresse par défaut utilisées pour la négociation du canal d'échange
state = False                       # Variable indiquant l'état du canal de communication (False : canal non négotié/ établi, True : canl en place et échange possible)

##          Fonction send :              ##
## Fonction prenant une string en entrée ##
## la string est encryptée puis envoyée  ##

def send(message):
    radio.send(message)             # taille maximal du message : 251
##              Fonction listen :           ##
## Fonction qui retourne une string         ##
## la string est récupérée puis décryptée   ##

def listen(address=None):
    if address != None:
        radio.config(address=address)
    m = radio.receive()
    return m

def manage(sig, state):
    if sig != None:
        sig = sig.split(";")                        # On découpe le message sur le séparateur choisi : ";"
        if sig[0] == initialize:
            print("initializing coms")              # Si un message init est reçu on renvoie un message accept en ajoutant l'adresse sur laquelle on souhaite communiquer
            send(accept+";0x10010011")
            return state                            # Le canal n'étant pas encore établie on ne change pas la valeur de state
        elif sig[0] == accept:
            print("accepting coms")
            if state == False:                      # Si l'on reçoit un message de type accept et que le canal de communication n'était pas encore établi
                send(accept+";0x10010011")          # On renvoie un accept avec l'adresse de communication et on configure le canal, enfin on passe state à True
            radio.config(address=int(sig[1]))

            state = True
            print("communication established")
            return state
    return state

radio.config(address=int(default_address))          # Configuration initiale : on configure le canal sur l'adresse par défaut et l'initialise (radio.config et radio.on)
radio.on()                                          # Et on intialise la connexion UART (USB) au serveur.
uart.init(baudrate=115200, bits=2048)

while True:                                         # C'est ici qu'est défini le comportement du Microbit
    message = listen()                              # On commence par récupérer un potentiel message et le passons à manage pour connaitre l'état du canal
    state = True
    print(message)
    if state == False:                              # Si le canal n'est pas encore établi on envoie un message d'init
        send(initialize)
    else:
        srvmsg = uart.readline()                    # Si le canal est établi :
        if srvmsg.decode('utf-8') == "TL":          # On écoute l'UART et vérifions la nature du message et l'existence
            send("message;TL")                      # On renvoie alors l'ordre au capteur
        if srvmsg.decode('utf-8') == "LT":
            send("message;LT")
        srvmsg = None

    if state and message != None:                   # Si un canal a déjà été établi et que nous avons reçu un message du capteur
        print(str(message))                         # Alors celui-ci est transmis au serveur


