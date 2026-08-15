# Realistic Aquatic Monitoring IoT Node (Wokwi ESP32 Digital Twin v3.0)

This system simulates a **multi-parameter aquatic environmental sensing station** designed for real-time watershed surveillance, industrial discharge detection, and ecological health monitoring.

---

## 1. Hardware Architecture & Sensor Classification

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   ESP32 AQUATIC IOT NODE                                        │
├─────────────────────────┬───────────────────┬───────────────────────────────┬───────────────────┤
│ Sensor Parameter        │ Wokwi Component   │ Physical Principle / Equation │ Real-World Equiv. │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 1. pH Level             │ Potentiometer 1   │ Analog Glass Electrode        │ Atlas Scientific  │
│                         │ (GPIO 34 ADC)     │ pH = (V / 3.3) * 14.0         │ EZO-pH Probe      │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 2. Turbidity            │ Potentiometer 2   │ Nephelometric Optical Scatter │ YSI EXO Turbidity │
│                         │ (GPIO 35 ADC)     │ FNU = (V / 3.3) * 300.0       │ Probe (860nm LED) │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 3. Dissolved Oxygen     │ Potentiometer 3   │ Galvanic / Luminescent DO     │ Vernier Optical   │
│                         │ (GPIO 32 ADC)     │ DO = (V / 3.3) * 14.0 mg/L    │ DO Sensor (ODO)   │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 4. Specific Conductance │ Potentiometer 4   │ 4-Electrode Toroidal Cell     │ Campbell Sci      │
│                         │ (GPIO 33 ADC)     │ SpCond = (V / 3.3) * 1500 µS  │ CS547A Probe      │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 5. Water Temperature    │ DS18B20 1-Wire    │ Direct Digital OneWire Bus    │ Waterproof digital│
│                         │ (GPIO 4 + 4.7kΩ)  │ tempSensors.getTempCByIndex() │ thermal probe     │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 6. Nutrient Proxy       │ Potentiometer 5   │ Electrochemical ISE Interface │ Hach ISE Nitrate/ │
│    (NO3 & PO4)          │ (GPIO 39 / VN)    │ NO3 = 0.1 + (ratio * 12.0)    │ Phosphate Analyzer│
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 7. Optical Biological   │ Potentiometer 6   │ In-situ Optical Fluorometer   │ Turner Designs    │
│    (Chlorophyll & fDOM) │ (GPIO 36 / VP)    │ Chl-a = 1.0 + (ratio * 40.0)  │ Cyclops-7F Fluor. │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 8. Heavy Metal Risk     │ Firmware Model    │ Acid leaching + conductivity  │ In-situ early     │
│    (Lead, Hg, As)       │ (Geochemical)     │ risk = (acid*0.5)+(ionic*0.35)│ warning proxy     │
├─────────────────────────┼───────────────────┼───────────────────────────────┼───────────────────┤
│ 9. Microbial Risk       │ Firmware Model    │ Thermal-sediment pathogen     │ E. coli risk      │
│    (E. coli Probability)│ (Bio-Thermal)     │ prob = turb*0.35 + temp*0.20  │ estimation model  │
└─────────────────────────┴───────────────────┴───────────────────────────────┴───────────────────┘
```

---

## 2. Hardware vs. Proxy Distinctions

### A. Simulated Physical Sensors
- **pH, Turbidity, Dissolved Oxygen, Specific Conductance, Temperature**:
  These simulate true analog front-end (AFE) conditioning boards and digital 1-Wire thermal sensors. In a real deployment, these map 1:1 to analog probes connected to instrument amplifiers or serial transmitters.

### B. Electrochemical & Optical Proxies
- **Nutrient Monitoring Proxy (NO3 & PO4)**:
  Ion-Selective Electrodes (ISE) output millivolts corresponding to logarithmic ion activity. The simulation converts voltage into realistic aquatic concentrations calibrated against NEON surface water data.
- **Optical Fluorometer Proxy (Chlorophyll-a & fDOM)**:
  In-situ fluorometers excite water samples with blue/UV light and measure emission at $685\text{ nm}$ (Chlorophyll) and $450\text{ nm}$ (fDOM). The simulation models this optical voltage response.

### C. Digital Twin Risk Models
- **Heavy Metal & Microbial Contamination Risk**:
  Heavy metal detection requires ICP-MS mass spectrometry and microbial quantification requires qPCR or incubation cultures. The IoT node calculates **derived biogeochemical risk indices** based on physical drivers (acid leaching kinetics, ionic conductivity spikes, organic matter complexation, and incubation temperatures). They are explicitly labeled as `[Estimated heavy metal risk]` and `[Estimated microbial risk]`.

---

## 3. Telemetry Payload Schema (`POST /predict`)

Dispatched every 5 seconds over WiFi:

```json
{
  "ph": 7.42,
  "turbidity": 4.5,
  "dissolved_oxygen": 8.65,
  "temperature": 21.3,
  "specific_conductance": 280.0,
  "nitrate_mg_l": 0.45,
  "phosphate_mg_l": 0.015,
  "chlorophyll_a_ug_l": 2.8,
  "heavy_metal_risk": 0.05,
  "microbial_risk": 8.5,
  "fdom": 22.0,
  "site_id": "WOKWI_SITE",
  "sensor_position": "001"
}
```

---

## 4. How to Run in Wokwi (Step-by-Step)

1. Open **[https://wokwi.com/projects/new/esp32](https://wokwi.com/projects/new/esp32)**.
2. In **`sketch.ino`**, replace all code with the contents of [`wokwi/sketch.ino`](file:///Users/raj/neon_water_project/wokwi/sketch.ino).
3. In **`diagram.json`**, replace all JSON with the contents of [`wokwi/diagram.json`](file:///Users/raj/neon_water_project/wokwi/diagram.json).
4. In **Library Manager**, add:
   - `ArduinoJson`
   - `OneWire`
   - `DallasTemperature`
5. Start your local FastAPI backend:
   ```bash
   .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```
6. Click **Play (▶)** in Wokwi!
7. **Interactive Scenario Testing**:
   - Turn any of the 6 potentiometers to adjust physical sensor voltages in real time.
   - Or click the **Green Pushbutton on GPIO 13** to cycle through 4 environmental scenarios:
     - `Scenario 0`: Live Potentiometer Mode
     - `Scenario 1`: Healthy Freshwater Ecosystem (`SAFE`)
     - `Scenario 2`: Eutrophication & Hypoxia Event (`WARNING` / `CRITICAL`)
     - `Scenario 3`: Industrial Contamination & Acid Dump (`CRITICAL`)
     - `Scenario 4`: Sensor Hardware Failure (`INSUFFICIENT_DATA`)
