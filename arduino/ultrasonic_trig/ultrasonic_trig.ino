const int trigPin = 5;
const int echoPin = 18;

#define SOUND_SPEED 0.034  // cm/us
#define TIMEOUT_US 30000   // 30ms timeout for pulseIn

long duration;
float distanceCm;

bool paused = false;
bool pauseMessageShown = false;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  if (paused) {
    if (!pauseMessageShown) {
      Serial.println("⏸️ Paused. Waiting for 'resume' command...");
      pauseMessageShown = true;
    }

    // Check if serial input available
    if (Serial.available()) {
      String input = Serial.readStringUntil('\n');
      input.trim();
      if (input == "resume") {
        paused = false;
        pauseMessageShown = false;
        Serial.println("✅ Resuming distance tracking...");
      }
    }

    delay(500);
    return;
  }

  // Trigger ultrasonic pulse
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read echo with timeout
  duration = pulseIn(echoPin, HIGH, TIMEOUT_US);
  if (duration == 0) {
    Serial.println("⚠️ No echo received (timeout).");
    delay(1000);
    return;
  }

  // Calculate distance
  distanceCm = duration * SOUND_SPEED / 2;

  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);

  // If object within range, send motion and pause
  if (distanceCm > 0 && distanceCm < 20) {
    Serial.println("motion");
    paused = true;
    pauseMessageShown = false;  // Reset message flag for next pause
    delay(2000); // Optional: debounce before next motion
  }

  delay(1000); // Stability delay
}
