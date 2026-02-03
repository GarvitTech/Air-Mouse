#include <Wire.h>
const int MPU_ADDR = 0x68;
const int LEFT_PIN = 4;
const int RIGHT_PIN = 5;
void setup() {
  Serial.begin(115200);
  pinMode(LEFT_PIN, INPUT_PULLUP);
  pinMode(RIGHT_PIN, INPUT_PULLUP);
  Wire.begin();
  delay(100);
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission(true);
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x1C);
  Wire.write(0x00);
  Wire.endTransmission(true)
  Serial.println("DEBUG MODE: Raw data output");
  Serial.println("Format: AccX,AccY,AccZ,Pitch,Roll,Left,Right");
}
void loop() {
  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_ADDR, 6, true);
  int16_t accX = Wire.read() << 8 | Wire.read();
  int16_t accY = Wire.read() << 8 | Wire.read();
  int16_t accZ = Wire.read() << 8 | Wire.read();
  float accX_g = accX / 16384.0;
  float accY_g = accY / 16384.0;
  float accZ_g = accZ / 16384.0;
  float pitch = atan2(-accX_g, sqrt(accY_g * accY_g + accZ_g * accZ_g)) * 180 / PI;
  float roll = atan2(accY_g, accZ_g) * 180 / PI;
  bool leftClick = !digitalRead(LEFT_PIN);
  bool rightClick = !digitalRead(RIGHT_PIN);
  Serial.print(accX);
  Serial.print(",");
  Serial.print(accY);
  Serial.print(",");
  Serial.print(accZ);
  Serial.print(",");
  Serial.print(pitch);
  Serial.print(",");
  Serial.print(roll);
  Serial.print(",");
  Serial.print(leftClick ? "1" : "0");
  Serial.print(",");
  Serial.print(rightClick ? "1" : "0");
  Serial.println();
  delay(100);
}
