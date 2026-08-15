/*
 * ==============================================================================
 *  SIH 2026 WATER INTELLIGENCE PLATFORM — AQUATIC MONITORING IOT NODE (v3.0)
 * ==============================================================================
 *
 *  Hardware Sensor Simulation Architecture:
 *    [Physicochemical Sensing]
 *      1. pH Sensor Module           (GPIO 34 ADC) : Glass electrode signal conditioner (0.0 - 14.0 pH)
 *      2. Turbidity Optical Sensor   (GPIO 35 ADC) : Nephelometric scatter detector (0.0 - 300.0 FNU/NTU)
 *      3. Dissolved Oxygen Sensor    (GPIO 32 ADC) : Galvanic / Optical DO transmitter (0.0 - 14.0 mg/L)
 *      4. Specific Conductance       (GPIO 33 ADC) : 4-Electrode toroidal cell (0.0 - 1500.0 µS/cm)
 *      5. Water Temperature Sensor   (GPIO 4 OneWire): Submersible DS18B20 digital probe (0.0 - 40.0 °C)
 *
 *    [Nutrient Sensing Interface (Electrochemical ISE Proxy)]
 *      6. Nutrient ISE Interface     (GPIO 39 / VN): Voltage conversion -> Nitrate (NO3) & Phosphate (PO4)
 *
 *    [Optical Biological Sensor (Fluorometer Proxy)]
 *      7. Optical Fluorometer        (GPIO 36 / VP): Optical fluorescence -> Chlorophyll-a (µg/L) & fDOM (QSU)
 *
 *    [Contamination & Microbial Environmental Models]
 *      8. Heavy Metal Contamination  : Geochemical proxy index (0.0 - 1.0) derived from pH, SpCond & fDOM
 *      9. Microbial Risk Index       : Pathogen proliferation model (0.0 - 100%) from Temp, Turbidity & DO
 *
 *  Target API Endpoint:
 *    POST http://host.wokwi.internal:8000/predict
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ── Network & Endpoint Configuration ──────────────────────────────
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* serverUrl = "http://host.wokwi.internal:8000/predict";

// ── Pin Allocations (ESP32 ADC1 Pins for WiFi Coexistence) ────────
const int PIN_PH_ADC       = 34; // ADC1_CH6: [Analog pH Sensor Module]
const int PIN_TURB_ADC     = 35; // ADC1_CH7: [Turbidity Optical Module]
const int PIN_DO_ADC       = 32; // ADC1_CH4: [Dissolved Oxygen Module]
const int PIN_COND_ADC     = 33; // ADC1_CH5: [Conductivity Transmitter]
const int PIN_NUTR_ADC     = 39; // ADC1_CH3 (VN): [Sensor Interface Proxy] Nutrients
const int PIN_BIO_ADC      = 36; // ADC1_CH0 (VP): [Sensor Interface Proxy] Fluorometer
const int PIN_ONEWIRE_TEMP = 4;  // GPIO 4: [Temperature Sensor Probe] DS18B20 1-Wire
const int PIN_SCENARIO_BTN = 13; // GPIO 13: [Scenario Selector] Pushbutton

// ── Hardware Status Indicator LEDs ────────────────────────────────
const int PIN_LED_SAFE     = 18; // Green LED: Normal & Safe status
const int PIN_LED_WARN     = 19; // Yellow LED: Warning / Elevated Risk
const int PIN_LED_CRIT     = 21; // Red LED: Critical / Action Required

// ── Peripheral Instances ──────────────────────────────────────────
OneWire oneWire(PIN_ONEWIRE_TEMP);
DallasTemperature tempSensors(&oneWire);

// ── Helper Function: Update Hardware Status LEDs ──────────────────
void set_hardware_status_leds(const char* status) {
  if (strcmp(status, "CRITICAL") == 0) {
    digitalWrite(PIN_LED_SAFE, LOW);
    digitalWrite(PIN_LED_WARN, LOW);
    digitalWrite(PIN_LED_CRIT, HIGH);
  } else if (strcmp(status, "WARNING") == 0) {
    digitalWrite(PIN_LED_SAFE, LOW);
    digitalWrite(PIN_LED_WARN, HIGH);
    digitalWrite(PIN_LED_CRIT, LOW);
  } else if (strcmp(status, "SAFE") == 0) {
    digitalWrite(PIN_LED_SAFE, HIGH);
    digitalWrite(PIN_LED_WARN, LOW);
    digitalWrite(PIN_LED_CRIT, LOW);
  } else {
    // INSUFFICIENT_DATA: Blinking yellow standby
    digitalWrite(PIN_LED_SAFE, LOW);
    digitalWrite(PIN_LED_WARN, HIGH);
    digitalWrite(PIN_LED_CRIT, LOW);
  }
}

// ── State & Timing Variables ──────────────────────────────────────
unsigned long lastTelemetryTime = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 5000;
unsigned long packetCounter = 0;

int currentScenario = 0;
int lastBtnState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY_MS = 250;

const char* SCENARIO_NAMES[] = {
  "0. Live Sensor Hardware Simulation (Analog Probes Active)",
  "1. Healthy Freshwater Ecosystem (Oligotrophic Pristine)",
  "2. Eutrophication Event (Nutrient Runoff & Algal Bloom)",
  "3. Industrial Chemical Contamination (Acid Shock & Heavy Metals)",
  "4. Sensor Failure / Telemetry Loss (Null Channels)"
};


// ══════════════════════════════════════════════════════════════════
//  SENSOR ACQUISITION & CALIBRATION FUNCTIONS
// ══════════════════════════════════════════════════════════════════

// 1. pH Glass Electrode Sensor Calibration (0 - 3.3V -> 0.0 - 14.0 pH)
float read_ph_sensor() {
  int raw = analogRead(PIN_PH_ADC);
  float voltage = (raw / 4095.0f) * 3.3f;
  float ph = (voltage / 3.3f) * 14.0f; // Linear Nernst response
  return constrain(ph, 0.0f, 14.0f);
}

// 2. Nephelometric Turbidity Sensor Calibration (0 - 3.3V -> 0.0 - 300.0 FNU)
float read_turbidity_sensor() {
  int raw = analogRead(PIN_TURB_ADC);
  float voltage = (raw / 4095.0f) * 3.3f;
  float turbidity = (voltage / 3.3f) * 300.0f; // Optical scatter response
  return constrain(turbidity, 0.0f, 300.0f);
}

// 3. Galvanic Dissolved Oxygen Sensor Calibration (0 - 3.3V -> 0.0 - 14.0 mg/L)
float read_do_sensor() {
  int raw = analogRead(PIN_DO_ADC);
  float voltage = (raw / 4095.0f) * 3.3f;
  float do_val = (voltage / 3.3f) * 14.0f; // Oxygen diffusion current
  return constrain(do_val, 0.0f, 14.0f);
}

// 4. Toroidal Specific Conductance Transmitter Calibration (0 - 3.3V -> 0 - 1500 µS/cm)
float read_conductivity_sensor() {
  int raw = analogRead(PIN_COND_ADC);
  float voltage = (raw / 4095.0f) * 3.3f;
  float cond = (voltage / 3.3f) * 1500.0f; // 4-Electrode cell constant
  return constrain(cond, 0.0f, 1500.0f);
}

// 5. DS18B20 Digital OneWire Temperature Sensor
float read_temperature_sensor() {
  tempSensors.requestTemperatures();
  float temp = tempSensors.getTempCByIndex(0);
  if (temp < -50.0f || temp > 100.0f) {
    temp = 21.5f; // Fallback baseline
  }
  return temp;
}

// 6. Electrochemical Nutrient ISE Interface (Voltage -> Nitrate & Phosphate)
void read_nutrient_proxy(float &nitrate_mg_l, float &phosphate_mg_l, float cond_val, float turb_val) {
  int raw = analogRead(PIN_NUTR_ADC);
  float nutr_voltage_ratio = raw / 4095.0f; // 0.0 to 1.0 electrochemical potential

  // Nitrate (NO3): Normal 0-2 mg/L, High >10 mg/L (EPA Drinking limit: 10 mg/L)
  nitrate_mg_l = 0.10f + (nutr_voltage_ratio * 12.0f) + (cond_val / 1500.0f) * 0.80f;

  // Phosphate (PO4): Normal 0-0.05 mg/L, High >0.10 mg/L (Eutrophic limit: 0.05 mg/L)
  phosphate_mg_l = 0.005f + (nutr_voltage_ratio * 0.35f) + (turb_val / 300.0f) * 0.05f;
}

// 7. Optical Fluorometer Biological Sensor (Voltage -> Chlorophyll-a & fDOM)
void read_optical_biological_proxy(float &chlorophyll_a_ug_l, float &fdom_qsu, float turb_val, float phosphate_mg_l) {
  int raw = analogRead(PIN_BIO_ADC);
  float bio_voltage_ratio = raw / 4095.0f; // Optical emission intensity

  // Chlorophyll-a: Low <10 µg/L, Moderate 10-30 µg/L, Bloom >30 µg/L
  chlorophyll_a_ug_l = 1.0f + (bio_voltage_ratio * 40.0f) + (phosphate_mg_l / 0.10f) * 2.0f;

  // fDOM (Fluorescent Dissolved Organic Matter): 15 - 180 QSU
  fdom_qsu = 15.0f + (bio_voltage_ratio * 50.0f) + (turb_val / 300.0f) * 30.0f;
}

// 8. Heavy Metal Contamination Risk Proxy (0.0 - 1.0 Index)
float compute_heavy_metal_risk(float ph_val, float cond_val, float fdom_val) {
  float acid_leaching = max(0.0f, (6.5f - ph_val) / 3.5f); // Lead/heavy metal pipe leaching in acidic water
  float ionic_shock   = cond_val / 1500.0f;                 // Industrial effluent conductivity
  float organic_metal = fdom_val / 180.0f;                  // Organo-metallic mercury complexation
  
  float risk = (acid_leaching * 0.50f) + (ionic_shock * 0.35f) + (organic_metal * 0.15f);
  return constrain(risk, 0.0f, 1.0f);
}

// 9. Microbial Risk Proliferation Model (0.0 - 100.0 %)
float compute_microbial_risk(float temp_val, float turb_val, float fdom_val, float do_val) {
  float temp_factor = constrain((temp_val - 15.0f) / 25.0f, 0.0f, 1.0f); // Warm incubator effect
  float turb_factor = constrain(turb_val / 200.0f, 0.0f, 1.0f);          // Sediment pathogen attachment
  float fdom_factor = constrain(fdom_val / 100.0f, 0.0f, 1.0f);          // Organic nutrient substrate
  float do_deficit  = constrain((8.0f - do_val) / 8.0f, 0.0f, 1.0f);     // Anaerobic conditions

  float prob = (turb_factor * 0.35f) + (fdom_factor * 0.30f) + (temp_factor * 0.20f) + (do_deficit * 0.15f);
  return constrain(prob * 100.0f, 0.0f, 100.0f);
}


// ══════════════════════════════════════════════════════════════════
//  SETUP & INITIALIZATION
// ══════════════════════════════════════════════════════════════════

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n================================================================================");
  Serial.println("   SIH WATER INTELLIGENCE — MULTI-DOMAIN AQUATIC MONITORING NODE (v3.0)");
  Serial.println("================================================================================");

  analogReadResolution(12);
  pinMode(PIN_SCENARIO_BTN, INPUT_PULLUP);
  pinMode(PIN_LED_SAFE, OUTPUT);
  pinMode(PIN_LED_WARN, OUTPUT);
  pinMode(PIN_LED_CRIT, OUTPUT);
  set_hardware_status_leds("SAFE"); // Initialize green standby

  tempSensors.begin();
  Serial.println("[HARDWARE] Multi-Channel 12-Bit ADC, Status LEDs & DS18B20 1-Wire Probe Initialized.");

  Serial.printf("[WIFI] Connecting to SSID: %s ", ssid);
  WiFi.begin(ssid, password);
  
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(400);
    Serial.print(".");
    retries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WIFI] Connected Successfully!");
    Serial.printf("[WIFI] Station IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[WIFI] Running in Simulation Standby Mode.");
  }

  Serial.printf("[API] Target Endpoint: %s\n", serverUrl);
  Serial.println("[TIP] Press the Green Button (GPIO 13) or type 0-4 in Serial to switch scenarios!");
  Serial.println("================================================================================\n");
}


// ══════════════════════════════════════════════════════════════════
//  MAIN LOOP: TELEMETRY ACQUISITION & TRANSMISSION
// ══════════════════════════════════════════════════════════════════

void loop() {
  unsigned long currentMillis = millis();

  // ── Pushbutton Scenario Switcher ────────────────────────────────
  int reading = digitalRead(PIN_SCENARIO_BTN);
  if (reading == LOW && lastBtnState == HIGH && (currentMillis - lastDebounceTime > DEBOUNCE_DELAY_MS)) {
    lastDebounceTime = currentMillis;
    currentScenario = (currentScenario + 1) % 5;
    Serial.printf("\n[SCENARIO SWITCHED VIA BUTTON] -> %s\n\n", SCENARIO_NAMES[currentScenario]);
  }
  lastBtnState = reading;

  // ── Serial Command Scenario Switcher ────────────────────────────
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c >= '0' && c <= '4') {
      currentScenario = c - '0';
      Serial.printf("\n[SCENARIO SWITCHED VIA SERIAL] -> %s\n\n", SCENARIO_NAMES[currentScenario]);
    }
  }

  // ── Periodic Telemetry Packet (Every 5 Seconds) ─────────────────
  if (currentMillis - lastTelemetryTime >= TELEMETRY_INTERVAL_MS) {
    lastTelemetryTime = currentMillis;
    packetCounter++;

    bool is_sensor_failure = false;
    float ph_val, turb_val, do_val, temp_val, cond_val, fdom_val;
    float nitrate_mg_l, phosphate_mg_l, chlorophyll_a_ug_l;
    float heavy_metal_risk, microbial_risk;

    if (currentScenario == 1) {
      // Scenario 1: Healthy Freshwater Ecosystem (Oligotrophic)
      ph_val             = 7.40f;
      do_val             = 8.80f;
      turb_val           = 3.2f;
      cond_val           = 220.0f;
      temp_val           = 19.5f;
      fdom_val           = 18.0f;
      nitrate_mg_l       = 0.45f;
      phosphate_mg_l     = 0.015f;
      chlorophyll_a_ug_l = 2.5f;
      heavy_metal_risk   = 0.05f;
      microbial_risk     = 8.5f;
    }
    else if (currentScenario == 2) {
      // Scenario 2: Eutrophication & Hypoxia Event (Algal Bloom)
      ph_val             = 8.65f;
      do_val             = 3.20f;
      turb_val           = 32.0f;
      cond_val           = 580.0f;
      temp_val           = 26.5f;
      fdom_val           = 75.0f;
      nitrate_mg_l       = 12.8f;
      phosphate_mg_l     = 0.185f;
      chlorophyll_a_ug_l = 42.0f;
      heavy_metal_risk   = 0.18f;
      microbial_risk     = 78.5f;
    }
    else if (currentScenario == 3) {
      // Scenario 3: Industrial Contamination Event (Acid Dump & Heavy Metals)
      ph_val             = 2.85f;
      do_val             = 2.10f;
      turb_val           = 145.0f;
      cond_val           = 1850.0f;
      temp_val           = 23.0f;
      fdom_val           = 160.0f;
      nitrate_mg_l       = 14.5f;
      phosphate_mg_l     = 0.280f;
      chlorophyll_a_ug_l = 15.0f;
      heavy_metal_risk   = 0.88f;
      microbial_risk     = 65.0f;
    }
    else if (currentScenario == 4) {
      // Scenario 4: Sensor Failure / Telemetry Loss
      is_sensor_failure = true;
      ph_val = 0.0f; do_val = 0.0f; turb_val = 0.0f; cond_val = 0.0f; temp_val = 0.0f; fdom_val = 0.0f;
      nitrate_mg_l = 0.0f; phosphate_mg_l = 0.0f; chlorophyll_a_ug_l = 0.0f;
      heavy_metal_risk = 0.0f; microbial_risk = 0.0f;
    }
    else {
      // Scenario 0: Live Real-Time Physical Sensor Conversions
      ph_val   = read_ph_sensor();
      turb_val = read_turbidity_sensor();
      do_val   = read_do_sensor();
      cond_val = read_conductivity_sensor();
      temp_val = read_temperature_sensor();

      // Read digital twin proxy interfaces
      read_nutrient_proxy(nitrate_mg_l, phosphate_mg_l, cond_val, turb_val);
      read_optical_biological_proxy(chlorophyll_a_ug_l, fdom_val, turb_val, phosphate_mg_l);

      // Compute multi-domain risk indices
      heavy_metal_risk = compute_heavy_metal_risk(ph_val, cond_val, fdom_val);
      microbial_risk   = compute_microbial_risk(temp_val, turb_val, fdom_val, do_val);
    }

    // ── Formatted Serial Monitor Diagnostic Output ─────────────────
    Serial.printf("\n[PACKET #%lu] Mode: %s\n", packetCounter, SCENARIO_NAMES[currentScenario]);
    Serial.println("================================================================================");
    Serial.println("                WATER QUALITY SENSOR NODE & AQUATIC DIGITAL TWIN");
    Serial.println("================================================================================");
    
    if (is_sensor_failure) {
      Serial.println("  ⚠️  [ALERT] TELEMETRY FAULT: SENSOR SIGNALS MISSING (NULL CHANNELS)  ⚠️");
    } else {
      Serial.println("[1. PHYSICAL SENSOR SIGNALS]");
      Serial.printf("  • pH Level (Glass Electrode)     : %6.2f pH\n", ph_val);
      Serial.printf("  • Turbidity (Optical Scatter)    : %6.2f FNU/NTU\n", turb_val);
      Serial.printf("  • Dissolved Oxygen (DO Sensor)   : %6.2f mg/L\n", do_val);
      Serial.printf("  • Water Temperature (DS18B20)    : %6.1f °C\n", temp_val);
      Serial.printf("  • Conductivity (Toroidal Cell)   : %6.1f µS/cm\n", cond_val);

      Serial.println("\n[2. NUTRIENT PROXY SENSING (ELECTROCHEMICAL ISE)]");
      Serial.printf("  • Nitrate (NO3 Concentration)    : %6.2f mg/L   (Normal: 0-2, High: >10 mg/L) [Proxy]\n", nitrate_mg_l);
      Serial.printf("  • Phosphate (PO4 Concentration)  : %6.3f mg/L   (Normal: 0-0.05, High: >0.1 mg/L) [Proxy]\n", phosphate_mg_l);

      Serial.println("\n[3. OPTICAL BIOLOGICAL SENSOR (FLUOROMETER PROXY)]");
      Serial.printf("  • Chlorophyll-a (Algal Biomass)  : %6.2f µg/L   (Bloom Risk: >30 µg/L) [Proxy]\n", chlorophyll_a_ug_l);
      Serial.printf("  • fDOM (Organic Carbon Load)     : %6.1f QSU    [Proxy]\n", fdom_val);

      Serial.println("\n[4. ESTIMATED CONTAMINATION & MICROBIAL RISKS]");
      Serial.printf("  • Heavy Metal Risk Index         : %6.2f [%s] [Estimated heavy metal risk]\n", 
                    heavy_metal_risk, heavy_metal_risk < 0.30f ? "LOW (0.0-0.3)" : (heavy_metal_risk < 0.70f ? "MODERATE (0.3-0.7)" : "HIGH (0.7-1.0)"));
      Serial.printf("  • Microbial Risk Index (E. coli) : %5.1f%% [%s] [Estimated microbial risk]\n", 
                    microbial_risk, microbial_risk < 25.0f ? "LOW / SAFE" : (microbial_risk < 65.0f ? "ELEVATED" : "HIGH PATHOGEN RISK"));
    }
    Serial.println("================================================================================");

    // ── Build JSON Telemetry Payload ───────────────────────────────
    StaticJsonDocument<896> jsonDoc;
    if (is_sensor_failure) {
      jsonDoc["ph"]                   = nullptr;
      jsonDoc["turbidity"]            = nullptr;
      jsonDoc["dissolved_oxygen"]     = nullptr;
      jsonDoc["temperature"]          = nullptr;
      jsonDoc["specific_conductance"] = nullptr;
      jsonDoc["nitrate_mg_l"]         = nullptr;
      jsonDoc["phosphate_mg_l"]       = nullptr;
      jsonDoc["chlorophyll_a_ug_l"]   = nullptr;
      jsonDoc["heavy_metal_risk"]     = nullptr;
      jsonDoc["microbial_risk"]       = nullptr;
      jsonDoc["fdom"]                 = nullptr;
    } else {
      jsonDoc["ph"]                   = round(ph_val * 100.0f) / 100.0f;
      jsonDoc["turbidity"]            = round(turb_val * 10.0f) / 10.0f;
      jsonDoc["dissolved_oxygen"]     = round(do_val * 100.0f) / 100.0f;
      jsonDoc["temperature"]          = round(temp_val * 10.0f) / 10.0f;
      jsonDoc["specific_conductance"] = round(cond_val * 10.0f) / 10.0f;
      jsonDoc["nitrate_mg_l"]         = round(nitrate_mg_l * 100.0f) / 100.0f;
      jsonDoc["phosphate_mg_l"]       = round(phosphate_mg_l * 1000.0f) / 1000.0f;
      jsonDoc["chlorophyll_a_ug_l"]   = round(chlorophyll_a_ug_l * 10.0f) / 10.0f;
      jsonDoc["heavy_metal_risk"]     = round(heavy_metal_risk * 100.0f) / 100.0f;
      jsonDoc["microbial_risk"]       = round(microbial_risk * 10.0f) / 10.0f;
      jsonDoc["fdom"]                 = round(fdom_val * 10.0f) / 10.0f;
    }
    jsonDoc["site_id"]              = "WOKWI_SITE";
    jsonDoc["sensor_position"]      = "001";

    String jsonPayload;
    serializeJson(jsonDoc, jsonPayload);

    Serial.println("[JSON DISPATCHED TO FASTAPI BACKEND]:");
    Serial.println(jsonPayload);

    // ── Dispatch HTTP POST Request ─────────────────────────────────
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(serverUrl);
      http.addHeader("Content-Type", "application/json");
      http.setTimeout(3000);

      int httpCode = http.POST(jsonPayload);

      if (httpCode > 0) {
        String response = http.getString();
        Serial.printf("\n[HTTP RESPONSE] Status: %d OK\n", httpCode);

        StaticJsonDocument<1024> respDoc;
        DeserializationError err = deserializeJson(respDoc, response);
        
        if (!err) {
          const char* final_stat = respDoc["final_status"] | "N/A";
          const char* anom_stat  = respDoc["anomaly_status"] | "N/A";
          float anom_score       = respDoc["anomaly_score"] | 0.0;
          float wqi              = respDoc["environmental_indicators"]["wqi"] | 0.0;
          const char* wqi_grade  = respDoc["environmental_indicators"]["wqi_grade"] | "N/A";
          const char* reason     = respDoc["override_reason"] | "";

          // Update physical status indicator LEDs on the circuit board
          set_hardware_status_leds(final_stat);

          Serial.println("  ┌────────────────────────────────────────────────────────┐");
          Serial.printf("  │  Final Operational Status : %-27s│\n", final_stat);
          Serial.printf("  │  Model 1 Anomaly Status   : %-27s│\n", anom_stat);
          Serial.printf("  │  Anomaly Severity Score   : %+26.4f │\n", anom_score);
          Serial.printf("  │  Water Quality Index (WQI): %5.1f/100 (%-18s)│\n", wqi, wqi_grade);
          Serial.println("  └────────────────────────────────────────────────────────┘");
          if (strlen(reason) > 0) {
            Serial.printf("  💡 AI Causal Reason: %s\n", reason);
          }
        }
      } else {
        Serial.printf("[HTTP] POST failed (Code: %d) — Payload simulated above.\n", httpCode);
      }
      http.end();
    }
    Serial.println("================================================================================\n");
  }
}
