#include <SPI.h>
#include <mrf24j.h>

const int pin_reset = 48;
const int pin_cs = 46; // default CS pin on ATmega8/168/328
const int pin_interrupt = 11; // default interrupt pin on ATmega8/168/328

Mrf24j mrf(pin_reset, pin_cs, pin_interrupt);


long last_time;
long tx_interval = 1000;

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial3.begin(9600);
  
  mrf.reset();
  mrf.init();
  
  mrf.set_pan(0xcafe);
  // This is _our_ address
  mrf.address16_write(0x6001); 


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
    //Serial.print("received a packet ");Serial.print(mrf.get_rxinfo()->frame_length, DEC);Serial.println(" bytes long");
    Serial.print("\n");
    if(mrf.get_bufferPHY()){
      // Serial.println("Packet data (PHY Payload):");
      for (int i = 0; i < mrf.get_rxinfo()->frame_length; i++) {
          Serial3.print(mrf.get_rxbuf()[i]);
        //  Serial.print(mrf.get_rxbuf()[i]);
        Serial.print(Serial1.read());

      }
    }
    
    // Serial.println("\r\nASCII data (relevant data):");
    for (int i = 0; i < mrf.rx_datalength(); i++) {
        Serial3.write(mrf.get_rxinfo()->rx_data[i]);
     //   Serial.write(mrf.get_rxinfo()->rx_data[i]);
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