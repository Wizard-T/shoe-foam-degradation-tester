/*
  ============================================================
  Midsole Compression Tester — v1 Prototype Firmware
  ============================================================

  Description:
    Drives a stepper motor through a controlled compression cycle
    on a running shoe's midsole while logging force (via HX711 +
    4-cell load cell bridge) and displacement (calculated from
    stepper step count) to produce a force-displacement curve.

  Hardware:
    - Arduino Uno
    - HX711 load cell amplifier + 4x 50kg load cells (summed bridge)
    - NEMA17 stepper motor (17HS4401)
    - TMC2209 stepper driver
    - T8 lead screw (2mm pitch) + 5mm-to-8mm flexible coupler

  Author:       Carson Templin
  Repo:         github.com/Wizard-T/shoe-foam-degradation-tester
  Created:      8/11/26
  Last updated: 8/12/26
  Version:      v1.0 — initial prototype

  Notes:
    Written for Arduino Uno
    Calibration factor must be obtained using seperate script and entered in here, will differ by hardware

  ============================================================
*/

#include <HX711.h>

HX711 platform;

const float CALIBRATION_FACTOR = 419.5; // MEASURE AND UPDATE DURING SETUP

const float VERTICAL_INCREMENT = 0.1; //in mm
float displacement = 0.0;
const int STEPS_PER_REV = 200;
const int MICROSTEPS_PER_STEP = 8;  // may change based on MS1/MS2 wiring from board to board
const float LEAD_SCREW_PITCH_MM = 2.0;
const float MICROSTEPS_PER_MM = (STEPS_PER_REV * MICROSTEPS_PER_STEP) / LEAD_SCREW_PITCH_MM;
const float MICROSTEPS = VERTICAL_INCREMENT * MICROSTEPS_PER_MM;
const int MAX_HOMING_STEPS = 5000; // tune this number
int homingSteps = 0;

  /*
  Lead screw pitch is 2mm, meaning rotating the lead screw once will move the compressor 2mm
  TMC2209 defaults to 8 microsteps (MS1/MS2 unconfigured, both at GND), meaning writing HIGH to the pin produces a microstep and 8 microsteps make 1 step
  1 step/8 microsteps rotates the motor 1.8 degrees
  1 microstep rotates the motor 0.225 degrees
  200 steps/rev
  1600 microsteps/rev
  1 step = 1/100 mm
  1 microstep = 1/800 mm
  */

float stiffness = 0.0;
float force = 0.0;

//pinout
const int DOUT_PIN = 2;
const int SCK_PIN = 3;
const int STEP_PIN = 4;
const int DIR_PIN = 5;


void setup() {///////////////////////////////////////////////////////////////////////////////

  //communication
  Serial.begin(115200);

  //load cells
  platform.begin(DOUT_PIN, SCK_PIN);
  platform.set_scale(CALIBRATION_FACTOR);
  platform.tare();

  //stepper controller
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);


  //homing
  force = readForceGrams();
  digitalWrite(DIR_PIN, HIGH); //stepper direction
  while(force < 25 && homingSteps < MAX_HOMING_STEPS){ //tune this number
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(200);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(200);
    force = readForceGrams();
    homingSteps++;
  }
  displacement = 0.0;

}/////////////////////////////////////////////////////////////////////////////////////////////

void loop() {////////////////////////////////////////////////////////////////////////////////

  force = readForceGrams();
  digitalWrite(DIR_PIN, HIGH); //stepper direction
  delayMicroseconds(500);
 
  while(force<10000){ //tune this number
    advancePlatform();  
    force = readForceGrams();
    Serial.print(displacement);
    Serial.print(",");
    Serial.println(force);
  }

  force = readForceGrams();
  stiffness = force / displacement;

  digitalWrite(DIR_PIN, LOW); //stepper direction
  delayMicroseconds(500);
  Serial.println();

  while(displacement>0){
    retractPlatform();  
    force = readForceGrams();
    Serial.print(displacement);
    Serial.print(",");
    Serial.println(force);
  }
  
  //stiffness report
  Serial.println();
  Serial.print("Stiffness: ");
  Serial.println(stiffness);

}/////////////////////////////////////////////////////////////////////////////////////////

float readForceGrams(){
  return platform.get_units(3); //number of measurements averaged
}

void advancePlatform(){
  for(int i=0; i<MICROSTEPS; i++){
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(500);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(500);
  }
  displacement += VERTICAL_INCREMENT;
}

void retractPlatform(){
  for(int i=0; i<MICROSTEPS; i++){
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(500);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(500);
  }
  displacement -= VERTICAL_INCREMENT;
}
