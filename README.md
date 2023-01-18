# IOT_project
Controller fourni par l'enseignant puis modifié
# Préambule 

La chaîne de communication commence par la réception des données récupérées par les capteurs d'incendie et de luminosité. Ces données sont ensuite envoyées via radio à une carte réceptrice qui transmettra les données reçues à une carte Lora.

La carte 1 possède le code arduino de récupération des différents capteurs ainsi que l’envoie des données. La carte 2 réceptionne les données et les envoie à la carte Lora.
# Carte 1
## Récupération capteur incendie
<code>
#define FLAME A0 // definition emplacement capteur
#define ANALOGPIN A0    //  led capteur


int fire = digitalRead(FLAME);// variable fire = lecture capteur flamme


  if( fire == HIGH)  // si capteur flamme à 1 alors incendie
  {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("State: Fire !");   
    fire = "f1";     // donnée qui sera transmise = f1
  }
  else
  {
    digitalWrite(LED_BUILTIN, LOW);  // Set the buzzer OFF
    Serial.println("State: Calm !");
    fire = "f0";    // donnée qui sera transmise = f0
   
  }
</code>
 
 
## Récupération capteur luminosité

<code>
 #include <Wire.h>            //luminosité
#include "Ambient2.h"       //luminosité
Opt3001 Ambient2;           //luminosité
float reading;              //luminosité
int light ;
void loop()
{
  // Wait for measurement
  while(Ambient2.is_Measuring()){
    //Serial.println("Waiting...");
    delay(50);
  }
  // Do we have overflow?


  int lux = Ambient2.measure_Lux();
  if (Ambient2.is_Overflow()){
     Serial.println("Overflow detected");
  }
  else{
     // Read the measurement
     reading = Ambient2.measure_Lux();
     Serial.print("Ambient light is: ");
     Serial.print(reading);
     Serial.println(" lux");
     if( reading < 5){        
        lux = "l0";
     }
     else{
       lux = "l1" ;      
     }
     delay(1000);
     
  }

</code>

 
 
## Emetteur radio MRF

<code>
include <SPI.h>   // Importation des librairies
#include <mrf24j.h>   // Importation des librairies
 
const int pin_reset = 48;   // configuration des pins de la carte micro bee click
const int pin_cs = 46; // configuration des pins de la carte micro bee click
const int pin_interrupt = 11; // configuration des pins de la carte micro bee click
 
Mrf24j mrf(pin_reset, pin_cs, pin_interrupt);      
 
  mrf.set_pan(0xcafe);   //definition canal d’échange
  // This is _our_ address
  mrf.address16_write(0x6002);  //adresse emetteur
void setup() {
  mrf.reset();   //initialisation
  mrf.init();   //initialisation
}
void loop() {
    mrf.check_flags(&handle_rx, &handle_tx);   
    unsigned long current_time = millis();
}
  mrf.check_flags(&handle_rx, &handle_tx);
    unsigned long current_time = millis();
    if (current_time - last_time > tx_interval) {
        last_time = current_time;    
        send = lux + fire;  
        Serial.println("en attente...");
        mrf.send16(0x6001, lux); //envoie variable lux à l'adresse 0x6001
        delay(1000);
        mrf.send16(0x6001, fire); //envoie variable fire à l'adresse 0x6001
        delay(1000);
    }
 
}
</code>
 
 
# Carte 2
## Recepteur radio MRF
<code>
include <SPI.h>   // Importation des librairies
#include <mrf24j.h>   // Importation des librairies
 
const int pin_reset = 48;   // configuration des pins de la carte micro bee click
const int pin_cs = 46; // configuration des pins de la carte micro bee click
const int pin_interrupt = 11; // configuration des pins de la carte micro bee click
 
Mrf24j mrf(pin_reset, pin_cs, pin_interrupt);      
long last_time;
long tx_interval = 1000;
 
void setup() {
  Serial.begin(9600);   //configuration baudrate Serial pour avoir visuel
  Serial3.begin(9600);   //configuration baudrate Serial3 donnée envoyé à la carte Lora
 
  mrf.reset();
  mrf.init();
 
  mrf.set_pan(0xcafe);   // definition canal d’echange
  // This is _our_ address
  mrf.address16_write(0x6001); // definition adresse recepteur
 
  attachInterrupt(0, interrupt_routine, CHANGE); // interrupt 0 equivalent to pin 2(INT0) on ATmega8/168/328
  last_time = millis();
  interrupts();
}
 
void interrupt_routine() {
    mrf.interrupt_handler(); // mrf24 object interrupt routine
}
 
void loop() {
    mrf.check_flags(&handle_rx, &handle_tx);
    unsigned long current_time = millis();
}
 void handle_rx() {
    Serial.print("\n");
    for (int i = 0; i < mrf.rx_datalength(); i++) {
        Serial3.write(mrf.get_rxinfo()->rx_data[i]); //affichage donnée reçu sur Serial3
        Serial.write(Serial1.read());  
    }
}
 void handle_tx() {
    if (mrf.get_txinfo()->tx_ok) {
        Serial.println("TX went ok, got ack");
    } else {
        Serial.print("TX failed after ");Serial.print(mrf.get_txinfo()->retries);Serial.println(" retries\n");
    }
}
 
</code> 
 
 
 
 
 
 
 
 

