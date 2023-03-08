/*

 * 
 * Typical pin layout used:
 * --------------------------------------
 * --------------------------------------
 *             MFRC522      Arduino Uno     
 * Signal      Pin          Pin           
 * --------------------------------------
 * RST/Reset   RST          8             
 * SPI SS      SDA(SS)      10            
 * SPI MOSI    MOSI         11 / ICSP-4   
 * SPI MISO    MISO         12 / ICSP-1   
 * SPI SCK     SCK          13 / ICSP-3  
 * --------------------------------------
 * --------------------------------------
 *             SG90      Arduino Uno 
 * Signal      Pin          Pin           
 * --------------------------------------
 *PWD/signal   Signal        9            
 *
 */

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 8

const int trig = 6;  // chân trig của HC-SR04
const int echo = 7;  // chân echo của HC-SR04

unsigned int Gia_tri_moi;
String choice;

MFRC522 rfid(SS_PIN, RST_PIN);  // Instance of the class

MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];

void setup() {
  Serial.begin(9600);
  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
  TCCR1A = 0;
  TCCR1B = 0;
  // RESET lại 2 thanh ghi
  DDRB |= (1 << PB1);
  // Đầu ra PB1 là OUTPUT ( pin 9)

  TCCR1A |= (1 << WGM11);
  TCCR1B |= (1 << WGM12) | (1 << WGM13);
  // chọn Fast PWM, chế độ chọn TOP_value tự do  ICR1
  TCCR1A |= (1 << COM1A1);
  // So sánh thường( none-inverting)

  TCCR1B |= (1 << CS11);
  // P_clock=16mhz/8=2mhz
  // mỗi P_clock bằng 1/2mhz= 0.5 us
  OCR1A = 1060;
  Gia_tri_moi = OCR1A;
  // Value=1060 , tương đương xung có độ rộng 1060*0.5us=530us (0.53ms)
  // Value=4820, tương đương xung có độ rộng 4820*0.5us=2410us (2,41ms)
  ICR1 = 40000;
  // xung răng cưa tràn sau 40000 P_clock, tương đương (20ms)
  set(4820);
  pinMode(trig, OUTPUT);  // chân trig sẽ phát tín hiệu
  pinMode(echo, INPUT);   // chân echo sẽ nhận tín hiệu
}

void loop() {
  if (Serial.available() != 0) {
    choice = Serial.readStringUntil('\r');
  }

  if (choice == "On"){
    choice = "Off";
    opendoor();
  }


  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if (!rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if (!rfid.PICC_ReadCardSerial())
    return;

  if (rfid.uid.uidByte[0] != nuidPICC[0] || rfid.uid.uidByte[1] != nuidPICC[1] || rfid.uid.uidByte[2] != nuidPICC[2] || rfid.uid.uidByte[3] != nuidPICC[3]) {
    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }
    printHex(rfid.uid.uidByte, rfid.uid.size);
    opendoor();
  }

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}


/**
 * Helper routine to dump a byte array as hex values to Serial. 
 */
void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? "0" : "");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
}

void set(unsigned int x) {
  if (Gia_tri_moi != x) {
    OCR1A = x;
    Gia_tri_moi = OCR1A;
  } else {
    return;  // thoát ngay
  }
  // x : 1060 - 4820
  //Độ rộng: 0.53ms - 2.41 ms
}

void opendoor() {
  set(1060);  // 0 độ
  delay(500);
  // bool tf = false;
  // while ((distance() < 50) || (distance() > 500)) {
  // while ((distance() < 0) || (distance() > 500)) {
  //   // Serial.println(distance());
  //   // delay(3000);
  // }
  // Serial.println(distance());
  set(4820);
}


int distance() {
  unsigned long duration;  // biến đo thời gian
  int distance1;           // biến lưu khoảng cách

  /* Phát xung từ chân trig */
  digitalWrite(trig, 0);  // tắt chân trig
  delayMicroseconds(2);
  digitalWrite(trig, 1);  // phát xung từ chân trig
  delayMicroseconds(5);   // xung có độ dài 5 microSeconds
  digitalWrite(trig, 0);  // tắt chân trig

  /* Tính toán thời gian */
  // Đo độ rộng xung HIGH ở chân echo.
  duration = pulseIn(echo, HIGH);
  // Tính khoảng cách đến vật.
  distance1 = int(duration / 2 / 29.412);
  delay(50);
  /* In kết quả ra Serial Monitor */
  return distance1;
}
