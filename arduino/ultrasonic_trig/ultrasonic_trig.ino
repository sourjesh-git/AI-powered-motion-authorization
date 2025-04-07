const int trigPin = 5;
const int echoPin = 18;

#define SOUND_SPEED 0.034
#define uS_TO_S_FACTOR 1000000ULL
#define TIME_TO_SLEEP 10  // seconds

long duration;
float distanceCm;

#include "esp_sleep.h"

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  delay(1000); // Give time for Serial to start
}

void loop() {
  // Trigger ultrasonic pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read echo
  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * SOUND_SPEED / 2;

  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);

  // If object detected within 20 cm, send trigger and sleep
  if (distanceCm > 0 && distanceCm < 20) {
    Serial.println("motion");

    // Enable deep sleep after motion
    Serial.println("Going to deep sleep for 10 seconds...");
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
    esp_deep_sleep_start();
  }

  delay(1000); // Just wait before the next read
}
