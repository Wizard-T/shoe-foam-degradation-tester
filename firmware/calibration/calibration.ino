#include <HX711.h>

HX711 platform;

const int KNOWN_WEIGHT = 5000; //IN GRAMS, UPDATE TO YOUR SPECIFIC WEIGHT (MAX 35,000 GRAMS / 35 KG)

//pinout
const int DOUT_PIN = 2;
const int SCK_PIN = 3;

void setup() {
  Serial.begin(115200);
  platform.begin(DOUT_PIN, SCK_PIN);
  platform.set_scale(1);
  platform.tare();
  Serial.print("No load reading: ");
  Serial.println(platform.get_units(5));

  Serial.println("Place item of known weight on platform: ");
  delay(10000); // 10 seconds, in milliseconds
  float weightRead = platform.get_units(5);
  Serial.print("Weight read: ");
  Serial.print(weightRead);
  Serial.println(" (no units)");

  float calibrationFactor = weightRead / KNOWN_WEIGHT;

  Serial.print("Time to check the accuracy of your calibration factor. Remove the item from the platform.");
  delay(10000); // 10 seconds, in milliseconds
  platform.set_scale(calibrationFactor);
  platform.tare();
  Serial.print("No load reading: ");
  Serial.println(platform.get_units(5));

  Serial.println("Replace item of known weight on platform: ");
  delay(10000); // 10 seconds, in milliseconds
  weightRead = platform.get_units(5);
  Serial.print("Weight read: ");
  Serial.print(weightRead);
  Serial.println(" grams");
  Serial.println("If this reading is accurate, your calibration factor is correct. If not, rerun this program and follow the directions closely.");

  Serial.print("Calibration factor: ");
  Serial.println(calibrationFactor);
  Serial.println("Save this number, to be hardcoded in firmware for your machine.");
  
}

void loop() {
}
