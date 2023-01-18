
#include <Wire.h>            //luminosité
#include "Ambient2.h"       //luminosité
Opt3001 Ambient2;           //luminosité
float reading;              //luminosité

#include <MQ135.h>          //radio
#include <SPI.h>            //radio
#include <mrf24j.h>         //radio

#define FLAME A0 // flamme
#define ANALOGPIN A1    //  flamme
#define RZERO 206.85    //  flamme

MQ135 gasSensor = MQ135(ANALOGPIN);


const int pin_reset = 48;
const int pin_cs = 46; // default CS pin on ATmega8/168/328
const int pin_interrupt = 11; // default interrupt pin on ATmega8/168/328
long last_time;
long tx_interval = 1000;

int fire ;
int light ;

int send;

Mrf24j mrf(pin_reset, pin_cs, pin_interrupt);


void setup()
{
  
  Serial.begin(9600);
  delay(100);
  
  Wire.begin();

  Serial.println("Demarrage...");
  Ambient2.begin(); 

  Ambient2.set_time800();
  Ambient2.start_continuous();

  Serial.println("Set Up phase");
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(FLAME, INPUT);//define FLAME input pin

  float rzero = gasSensor.getRZero();

  // GAZ
  Serial.print("MQ135 RZERO Calibration Value : ");
  Serial.println(rzero);

    
  mrf.reset();
  mrf.init();
  
  mrf.set_pan(0xcafe);
  // This is _our_ address
  mrf.address16_write(0x6002); 


  attachInterrupt(0, interrupt_routine, CHANGE); // interrupt 0 equivalent to pin 2(INT0) on ATmega8/168/328
  last_time = millis();
  interrupts();

}

void interrupt_routine() {
    mrf.interrupt_handler(); // mrf24 object interrupt routine
}


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
  
   int fire = digitalRead(FLAME);// read FLAME sensor

  if( fire == HIGH)
  {
    digitalWrite(LED_BUILTIN, HIGH);
    Serial.println("State: Fire !");
    fire = "f1";
    //mrf.send16(0x6001, fire);      
  }
  else
  {
    digitalWrite(LED_BUILTIN, LOW);  // Set the buzzer OFF
    Serial.println("State: Calm !");
    fire = "f0";
    //mrf.send16(0x6001, fire);  
    // Flame sensor code for Robojax.com
    
  }
  float ppm = gasSensor.getPPM();
  //Serial.print("CO2_ppm:");
  //Serial.println(ppm);
  delay(1000);
  //Serial.println("");

    mrf.check_flags(&handle_rx, &handle_tx);
    unsigned long current_time = millis();
    if (current_time - last_time > tx_interval) {
        last_time = current_time;    
        send = lux + fire;   
        Serial.println("en attente...");
        mrf.send16(0x6001, lux);
        delay(1000);
        mrf.send16(0x6001, fire);
        delay(1000);
    }
  
}

void handle_rx() {
    Serial.print("received a packet ");Serial.print(mrf.get_rxinfo()->frame_length, DEC);Serial.println(" bytes long");
    
    if(mrf.get_bufferPHY()){
      Serial.println("Packet data (PHY Payload):");
      for (int i = 0; i < mrf.get_rxinfo()->frame_length; i++) {
          Serial.print(mrf.get_rxbuf()[i]);
      }
    }
    
    Serial.println("\r\nASCII data (relevant data):");
    for (int i = 0; i < mrf.rx_datalength(); i++) {
        Serial.write(mrf.get_rxinfo()->rx_data[i]);
    }
    
    Serial.print("\r\nLQI/RSSI=");
    Serial.print(mrf.get_rxinfo()->lqi, DEC);
    Serial.print("/");
    Serial.println(mrf.get_rxinfo()->rssi, DEC);
}

void handle_tx() {
    if (mrf.get_txinfo()->tx_ok) {
        Serial.println("TX went ok, got ack");
    } else {
        Serial.print("TX failed after ");Serial.print(mrf.get_txinfo()->retries);Serial.println(" retries\n");
    }
}