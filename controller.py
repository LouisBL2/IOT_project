# Program to control passerelle between Android application
# and micro-controller through USB tty
import time
import argparse
import signal
import sys
import socket
import socketserver
import serial
import threading
import datetime


HOST           = "0.0.0.0"
UDP_PORT       = 10000
MICRO_COMMANDS = ["TL" , "LT"]
FILENAME        = "values.txt"
LAST_VALUE      = ""



#Gestion des echanges avec l'application 
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        LAST_VALUE_data=str(LAST_VALUE)
        data = data.decode("utf-8")
        print("{}: Le client: {}, a envoyé: {}".format(current_thread.name, self.client_address, data))
        if (data != "") and (LAST_VALUE_data != ""):   #test pour empécher d'envoyer un message si LastValue est vide
                        if data in MICRO_COMMANDS: # Envoie du message d'ordre d'affichage a la passerelle microbit
                                if isinstance(data, str):
                                    data = data.encode()
                                sendUARTMessage(data)
                                
                        elif data == "getValues()": # Envoie de la dernière valeur reçu par le microbit à l'appli
                                if isinstance(LAST_VALUE_data, str):
                                    print("Envoie du message "+ LAST_VALUE_data + " à l'application")
                                socket.sendto(LAST_VALUE_data.encode(),self.client_address)
                        else:
                                print("Unknown message: ",data)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass



SERIALPORT = "/dev/ttyACM0" 
BAUDRATE = 115200
ser = serial.Serial()

def initUART():        

        ser.port=SERIALPORT
        ser.baudrate=BAUDRATE
        ser.bytesize = serial.EIGHTBITS #number of bits per bytes
        ser.parity = serial.PARITY_NONE #set parity check: no parity
        ser.stopbits = serial.STOPBITS_ONE #number of stop bits
        ser.timeout = None          #block read


        ser.xonxoff = False     #disable software flow control
        ser.rtscts = False     #disable hardware (RTS/CTS) flow control
        ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
        #ser.writeTimeout = 0     #timeout for write
        print('Starting Up Serial Monitor')
        try:
                ser.open()
        except serial.SerialException:
                print("Serial {} port not available".format(SERIALPORT))
                exit()


#Fonction d'envoie du message au micro controlleur passerelle
def sendUARTMessage(msg):
    ser.write(msg)
    msg = msg.decode('utf-8')
    print("Message <" + msg + "> envoyé a la passerelle microbit." )


# Main program logic follows:
if __name__ == '__main__':
        initUART()
        f= open(FILENAME,"a")
        print ('Press Ctrl-C to quit.')

        server = ThreadedUDPServer((HOST, UDP_PORT), ThreadedUDPRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True


        try:
                server_thread.start()
                print("Server started at {} port {}".format(HOST, UDP_PORT))
                while ser.isOpen() : 
                        if (ser.inWaiting() > 0): # if incoming bytes are waiting 
                                data_str = ser.readline()
                                if str(data_str) != "None" :
                                        f.write(str(data_str, 'UTF-8')+"\n")
                                LAST_VALUE = data_str.decode()


                                data_str = (str(data_str, 'UTF-8'))





        except (KeyboardInterrupt, SystemExit):
                server.shutdown()
                server.server_close()
                f.flush()
                f.close() 
                ser.close()
                exit()
