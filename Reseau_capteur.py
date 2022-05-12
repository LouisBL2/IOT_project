from microbit import *
import radio
from ssd1306 import initialize, clear_oled
from ssd1306_text import add_text
incomming
init = "micro_req"              # Message signifiant qu'un Microbit veut démarrer la communication
accept = "micro_acc"            # Message signifiant que le Microbit accepte la communication (permet de valider le passage à la nouvelle adresse de communication)
default_address = "0x90548090"  # adresse par défaut utilisées pour la négociation du canal d'échange
state = False         # Variable indiquant l'état du canal de communication (False : canal non négotié/ établi, True : canl en place et échange possible)

##          Fonction send :              ##
## Fonction prenant une string en entrée ##
## la string est envoyée  ##

def send(message):
    radio.send(message)


def listen(address=None):
    if address != None:
        radio.config(address=address)
    m = radio.receive()
    return m


def manage(sig, state):
    if sig != None:
        sig = sig.split(";")    # On découpe le message sur le séparateur choisi : ";"
        if sig[0] == init:
            print("initializing coms")
            send(accept+";0x10010011")      # Si un message init est reçu on renvoie un message accept en ajoutant l'adresse sur laquelle on souhaite communiquer
            return state                    # Le canal n'étant pas encore établie on ne change pas la valeur de state
        elif sig[0] == accept:
            print("accepting coms")
            if state == False:              # Si l'on reçoit un message de type accept et que le canal de communication n'était pas encore établi
                send(accept+";0x10010011")  # On renvoie un accept avec l'adresse de communication et on configure le canal, enfin on passe state à True
            radio.config(address=int(sig[1]))

            state = True
            print("communication established")
            return state
    return state

radio.config(address=int(default_address))
radio.on()                                  # Configuration initiale : on configure le canal sur l'adresse par défaut et l'initialise (radio.config et radio.on)
initialize(pinReset=pin0)                  # Ensuite on démarre l'écran pour préparer l'affichage


while True:                                 # C'est ici qu'est défini le comportement du Microbit
    message = listen()
    state = manage(message, state)          # On commence par récupérer un potentiel message et le passons à manage pour connaitre l'état du canal

    if state == False:
        send(init)                          # Si le canal n'est pas encore établi on envoie un message d'init

    if state and message != None:
        message = message.split(";")        #Si on a bien message de récupérer ainsi qu'un état de définit :
        if message[1] == "TL":                                                      # On découpe le message sur le séparateur choisi : ";"
            clear_oled()
            add_text(0, 0, "Temp : "+str(temperature()))                            # On vérifie l'ordre d'affichage demandé puis efface l'écran et affiche les données comme demandé
            add_text(0, 1, "Lum : "+str(display.read_light_level()))
            send("TL;"+str(temperature())+";"+str(display.read_light_level()))      # Enfin on envoie ces données à la passerelle dans le forma suivant : "<Ordre d'affichage>;<DATA>;<DATA>
        if message[1] == "LT":                                                      #<DATA> représentant des valeurs lues sur les capteurs
            clear_oled()
            add_text(0, 0, "Lum : "+str(display.read_light_level()))
            add_text(0, 1, "Temp : "+str(temperature()))
            send("LT;"+str(display.read_light_level())+";"+str(temperature()))
