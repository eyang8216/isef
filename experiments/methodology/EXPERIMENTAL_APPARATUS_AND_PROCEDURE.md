# Taylor Cone Experimental Validation - Detailed Apparatus and Procedure

**Project:** Lightweight Taylor-Cone Solver Experimental Validation  
**Authors:** Ethan Yang, Elliot Dong, Curtis Lau  
**Institution:** Independent Schools Foundation Academy, Hong Kong SAR  
**Document Purpose:** Complete experimental setup guide with budget, suppliers, and safety protocols

---

## Table of Contents

1. [Complete Apparatus List with Budget](#complete-apparatus-list-with-budget)
2. [Supplier Information](#supplier-information)
3. [Detailed Setup Procedure](#detailed-setup-procedure)
4. [Safety Protocols and Risk Mitigation](#safety-protocols-and-risk-mitigation)
5. [Step-by-Step Experimental Protocol](#step-by-step-experimental-protocol)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Emergency Procedures](#emergency-procedures)

---

## Complete Apparatus List with Budget

### **1. High Voltage Power Supply**

**Primary Option: Current-Limited Lab Supply**
- **Item:** Glassman High Voltage PS/EH Series (0-10 kV, 1-2 mA)
- **Specifications:**
  - Output: 0-10,000 V DC
  - Current limit: 1-2 mA (critical for safety)
  - Regulation: ±0.01%
  - Digital display and remote control
- **Cost:** ~$1,500-2,500 USD
- **Supplier:** Glassman High Voltage (glassmanHV.com), Newark Electronics, Mouser
- **Safety features:** Hardware current limiting, emergency shutdown, discharge circuit

**Alternative Option: More Affordable**
- **Item:** Spellman SL Series (0-5 kV, 1 mA)
- **Cost:** ~$800-1,200 USD
- **Supplier:** Spellman HV Electronics, eBay (used units)

**Budget Option: Regulated Flyback Module**
- **Item:** XP Power CA/CB Series with external current limiter
- **Cost:** ~$200-400 USD
- **Supplier:** DigiKey, Mouser
- **Note:** Requires additional enclosure and safety circuitry

**Recommended:** Glassman or Spellman for lab safety compliance

---

### **2. Syringe Pump**

**Primary Option: Precision Syringe Pump**
- **Item:** Harvard Apparatus PHD 2000 or PHD ULTRA
- **Specifications:**
  - Flow rate range: 0.001 µL/h to 220 mL/h
  - Accuracy: ±0.5%
  - Compatible with 0.5-60 mL syringes
- **Cost:** ~$2,000-3,500 USD
- **Supplier:** Harvard Apparatus (harvardapparatus.com), VWR

**Alternative Option: More Affordable**
- **Item:** New Era NE-300 Single Syringe Pump
- **Specifications:**
  - Flow rate: 0.73 µL/h to 2120 mL/h
  - Accuracy: ±1%
- **Cost:** ~$800-1,200 USD
- **Supplier:** New Era Pump Systems (syringepump.com)

**Budget Option: DIY Stepper Motor Pump**
- **Item:** Stepper motor + lead screw + Arduino control
- **Cost:** ~$150-300 USD
- **Supplier:** Parts from Amazon, Adafruit
- **Note:** Requires calibration and flow verification

**Recommended:** New Era NE-300 (good balance of cost and precision)

---

### **3. Camera and Imaging System**

**Primary Option: High-Speed CMOS Camera**
- **Item:** FLIR Blackfly S USB3 (BFS-U3-32S4M-C)
- **Specifications:**
  - Resolution: 2048×1536 pixels
  - Frame rate: 118 fps at full resolution
  - Sensor: Sony IMX252 (3.45 µm pixel)
  - Interface: USB 3.0
- **Cost:** ~$600-900 USD
- **Supplier:** FLIR (flir.com), Edmund Optics

**Alternative Option: Mid-Range USB Camera**
- **Item:** ELP USB Camera (5MP, 2592×1944)
- **Specifications:**
  - Resolution: 5MP
  - Frame rate: 15-30 fps
  - Manual focus
- **Cost:** ~$80-150 USD
- **Supplier:** Amazon, AliExpress

**Budget Option: Webcam with Macro Lens**
- **Item:** Logitech C920 + macro lens adapter
- **Cost:** ~$100-150 USD
- **Supplier:** Amazon, Best Buy
- **Note:** Limited resolution but sufficient for proof-of-concept

**Recommended:** FLIR Blackfly S (research-grade) or ELP camera (budget)

---

### **4. Macro Lens and Optics**

**Primary Option: Telecentric Lens**
- **Item:** Edmund Optics Techspec Telecentric Lens (0.5X)
- **Specifications:**
  - Magnification: 0.5X
  - Working distance: 110 mm
  - Distortion: <0.1%
- **Cost:** ~$1,200-2,000 USD
- **Supplier:** Edmund Optics (edmundoptics.com)

**Alternative Option: Macro Lens**
- **Item:** 25mm C-Mount Lens (F1.4, manual focus)
- **Specifications:**
  - Focal length: 25 mm
  - Aperture: F1.4-F16
  - Mount: C-mount (adapter for USB cameras)
- **Cost:** ~$40-80 USD
- **Supplier:** Amazon, Adafruit

**Extension Tubes (if using macro lens):**
- **Item:** C-mount extension tube set (5, 10, 20 mm)
- **Cost:** ~$30-50 USD
- **Supplier:** Amazon

**Recommended:** 25mm C-mount lens + extension tubes (good balance)

---

### **5. LED Backlight**

**Primary Option: Diffuse LED Panel**
- **Item:** Genaray LED SpectroLED Essential 240 Daylight
- **Specifications:**
  - Power: 25W
  - Color temperature: 5600K (daylight)
  - Dimmable
  - Size: 30×30 cm
- **Cost:** ~$100-200 USD
- **Supplier:** B&H Photo (bhphotovideo.com), Amazon

**Alternative Option: LED Light Pad**
- **Item:** Huion A4 LED Light Pad (used for tracing)
- **Specifications:**
  - Size: A4 (21×30 cm)
  - Dimmable
  - Even illumination
- **Cost:** ~$30-60 USD
- **Supplier:** Amazon

**Budget Option: DIY LED Panel**
- **Components:**
  - White LED strip (5630 SMD, 5m)
  - Diffusion sheet (acrylic or tracing paper)
  - 12V power supply
- **Cost:** ~$20-40 USD
- **Supplier:** Amazon, local electronics store

**Recommended:** Huion light pad (affordable, effective)

---

### **6. Mechanical Components**

#### **6.1 Needles and Nozzles**

**Stainless Steel Hypodermic Needles:**
- **Item:** Blunt-tip dispensing needles (various gauges)
- **Sizes to purchase:**
  - 21 gauge (0.80 mm OD, 0.51 mm ID)
  - 23 gauge (0.64 mm OD, 0.33 mm ID)
  - 25 gauge (0.51 mm OD, 0.26 mm ID)
- **Quantity:** Pack of 25 per size
- **Cost:** ~$15-30 per pack
- **Supplier:** McMaster-Carr, Amazon, Fisher Scientific

**Recommended starter:** 21 gauge (easier to observe)

#### **6.2 Extractor Electrode**

**Option 1: Stainless Steel Plate**
- **Item:** 304 stainless steel sheet (5×5 cm, 1 mm thick)
- **Cost:** ~$10-20
- **Supplier:** McMaster-Carr, local metal supplier
- **Preparation:** Polish surface, drill mounting holes

**Option 2: Copper Plate**
- **Item:** Copper sheet (5×5 cm, 1 mm thick)
- **Cost:** ~$8-15
- **Supplier:** McMaster-Carr, Amazon
- **Note:** Easier to machine than steel

**Option 3: PCB as Electrode**
- **Item:** Blank FR4 PCB with copper cladding (10×10 cm)
- **Cost:** ~$5-10
- **Supplier:** Amazon, electronics store
- **Note:** Pre-drilled holes available

**Recommended:** Copper plate (easy to work with)

#### **6.3 Positioning Hardware**

**Optical Breadboard:**
- **Item:** Aluminum breadboard (30×45 cm, M6 threading)
- **Cost:** ~$80-150 USD
- **Supplier:** Thorlabs, Edmund Optics, AliExpress

**Optical Posts and Holders:**
- **Items needed:**
  - 4× Optical posts (150-300 mm height)
  - 4× Post holders with clamping
  - 2× Right-angle clamps
  - 1× XY translation stage
- **Cost:** ~$150-300 USD total
- **Supplier:** Thorlabs, Edmund Optics

**Budget Alternative: DIY Frame**
- **Materials:**
  - Aluminum extrusion (20×20 mm, 2m total)
  - Corner brackets
  - 3D printed parts for mounts
- **Cost:** ~$50-100 USD
- **Supplier:** Amazon, Misumi, 8020.net

**Recommended:** Optical breadboard setup (professional, adjustable)

#### **6.4 Micrometer Stages**

**Linear Translation Stage:**
- **Item:** Manual linear stage (travel 25-50 mm)
- **Specifications:**
  - Resolution: 10 µm per division
  - Load capacity: 2-5 kg
- **Cost:** ~$60-120 USD
- **Supplier:** Amazon, AliExpress (Newport clones)

**Quantity needed:** 2 stages (one for electrode spacing, one for camera focus)

---

### **7. Enclosure and Safety**

#### **7.1 Faraday Cage / Safety Enclosure**

**Option 1: Metal Cabinet**
- **Item:** Hoffman CSD Series Steel Cabinet
- **Size:** 60×60×90 cm (24×24×36 inches)
- **Features:**
  - Grounded metal construction
  - Locking door with interlock switch
  - Ventilation slots
- **Cost:** ~$300-600 USD
- **Supplier:** Hoffman Enclosures, Grainger

**Option 2: Acrylic Box with Wire Mesh**
- **Materials:**
  - Acrylic sheets (6 mm thick) for frame
  - Copper wire mesh (grounded)
  - Hinged door with interlock
- **Cost:** ~$150-250 USD
- **Supplier:** Local plastics supplier, McMaster-Carr

**Budget Option: Cardboard + Aluminum Foil**
- **Not recommended for actual use** - only for early concept testing
- **Cost:** ~$20-40 USD

**Recommended:** Metal cabinet with proper interlock

#### **7.2 Interlock Switch**

**Safety Interlock:**
- **Item:** Magnetic safety switch (door interlock)
- **Specifications:**
  - Normally open contact
  - Rated for 24V DC control circuit
- **Cost:** ~$20-40 USD
- **Supplier:** Amazon, McMaster-Carr

**Wiring:** Connect in series with HV power supply enable line

#### **7.3 Warning Labels**

**High Voltage Warning Signs:**
- **Item:** ANSI Z535 compliant HV warning labels
- **Quantity:** 4-6 labels
- **Cost:** ~$10-20
- **Supplier:** Amazon, SafetySign.com

**Emergency Shutdown Button:**
- **Item:** Red mushroom emergency stop button (22mm)
- **Cost:** ~$10-20
- **Supplier:** Amazon, DigiKey

---

### **8. Fluids and Consumables**

#### **8.1 Test Liquids**

**Ethanol (190 proof or absolute):**
- **Item:** Laboratory grade ethanol
- **Volume:** 500 mL
- **Properties:**
  - Surface tension: ~22 mN/m
  - Conductivity: ~1 µS/cm (add dopant)
- **Cost:** ~$30-50
- **Supplier:** Fisher Scientific, VWR, Sigma-Aldrich

**Propylene Carbonate:**
- **Item:** Anhydrous, 99.7%
- **Volume:** 100 mL
- **Properties:**
  - Surface tension: ~41 mN/m
  - High permittivity: εᵣ ≈ 65
- **Cost:** ~$40-70
- **Supplier:** Sigma-Aldrich, TCI Chemicals

**Sodium Chloride (dopant):**
- **Item:** NaCl, ACS reagent grade
- **Amount:** 100 g
- **Purpose:** Increase conductivity to ~100-1000 µS/cm
- **Cost:** ~$15-25
- **Supplier:** Fisher Scientific, local chemical supplier

#### **8.2 Syringes and Tubing**

**Syringes:**
- **Item:** BD Luer-Lok plastic syringes (5 mL, 10 mL)
- **Quantity:** 10 of each
- **Cost:** ~$20-40
- **Supplier:** Fisher Scientific, Amazon

**PTFE Tubing:**
- **Item:** PTFE tubing (1/16" ID, 1/8" OD)
- **Length:** 2 meters
- **Cost:** ~$20-30
- **Supplier:** McMaster-Carr, Amazon

**Luer Fittings:**
- **Item:** Luer-to-tubing connectors (male/female)
- **Quantity:** Pack of 10
- **Cost:** ~$15-25
- **Supplier:** Cole-Parmer, Amazon

---

### **9. Electrical and Control**

#### **9.1 Multimeter**

**Digital Multimeter:**
- **Item:** Fluke 115 or similar
- **Specifications:**
  - DC voltage: up to 600V (for monitoring tap)
  - Resistance, continuity
- **Cost:** ~$100-180 USD
- **Supplier:** Amazon, Newark

**High Voltage Probe (optional):**
- **Item:** 1000:1 HV probe
- **Cost:** ~$150-300 USD
- **Supplier:** Tektronix, Fluke

#### **9.2 Grounding**

**Grounding Wire:**
- **Item:** 12 AWG stranded copper wire (green)
- **Length:** 5 meters
- **Cost:** ~$10-20
- **Supplier:** Hardware store, McMaster-Carr

**Ground Lugs and Clamps:**
- **Item:** Ring terminals and alligator clips
- **Cost:** ~$10-15
- **Supplier:** Hardware store, Amazon

---

### **10. Calibration Tools**

**Digital Calipers:**
- **Item:** Mitutoyo or similar (0-150 mm range)
- **Resolution:** 0.01 mm
- **Cost:** ~$60-120 USD
- **Supplier:** Amazon, McMaster-Carr

**Calibration Target:**
- **Option 1:** Precision machined scale (1951 USAF resolution target)
- **Cost:** ~$80-150 USD
- **Supplier:** Edmund Optics

**Option 2: Printed Scale**
- **Item:** High-res printed scale on transparency film
- **Cost:** ~$10-20 USD (printing service)

---

### **11. Personal Protective Equipment (PPE)**

**Electrical Safety Gloves:**
- **Item:** Class 0 insulated rubber gloves (rated to 1000V)
- **Cost:** ~$50-100 USD per pair
- **Supplier:** Grainger, Amazon

**Safety Glasses:**
- **Item:** ANSI Z87.1 rated safety glasses
- **Cost:** ~$10-20 per pair
- **Supplier:** Hardware store, Amazon

**Lab Coat:**
- **Item:** Cotton or synthetic lab coat
- **Cost:** ~$20-40
- **Supplier:** Fisher Scientific, Amazon

**Nitrile Gloves:**
- **Item:** Disposable nitrile gloves (box of 100)
- **Cost:** ~$15-25
- **Supplier:** Pharmacy, Amazon

---

## Budget Summary

### **Option 1: Research-Grade Setup ($7,000-10,000 USD)**

| Component | Cost (USD) |
|-----------|-----------|
| Glassman HV Power Supply | $2,000 |
| Harvard Apparatus Syringe Pump | $2,500 |
| FLIR Blackfly Camera | $800 |
| Telecentric Lens | $1,500 |
| LED Backlight | $150 |
| Optical Breadboard Setup | $500 |
| Metal Enclosure + Safety | $500 |
| Needles, Electrodes, Hardware | $300 |
| Chemicals and Consumables | $200 |
| PPE and Safety Equipment | $200 |
| Calibration Tools | $150 |
| Miscellaneous | $200 |
| **Total** | **~$9,000** |

---

### **Option 2: Mid-Range Setup ($3,000-4,000 USD)**

| Component | Cost (USD) |
|-----------|-----------|
| Spellman HV Power Supply | $1,000 |
| New Era NE-300 Syringe Pump | $1,000 |
| ELP USB Camera | $120 |
| C-Mount Macro Lens + Extensions | $80 |
| Huion LED Light Pad | $50 |
| Optical Breadboard Setup | $400 |
| Metal Enclosure + Safety | $400 |
| Needles, Electrodes, Hardware | $250 |
| Chemicals and Consumables | $150 |
| PPE and Safety Equipment | $150 |
| Calibration Tools | $100 |
| Miscellaneous | $150 |
| **Total** | **~$3,850** |

---

### **Option 3: Budget Setup ($1,200-1,800 USD)**

| Component | Cost (USD) |
|-----------|-----------|
| XP Power HV Module + Limiter | $300 |
| DIY Arduino Syringe Pump | $200 |
| Logitech C920 + Macro Adapter | $130 |
| DIY LED Panel | $35 |
| DIY Aluminum Frame | $80 |
| Acrylic Box + Wire Mesh | $180 |
| Needles, Electrodes, Hardware | $150 |
| Chemicals and Consumables | $120 |
| PPE and Safety Equipment | $120 |
| Digital Calipers | $60 |
| Miscellaneous | $100 |
| **Total** | **~$1,475** |

---

## Supplier Information

### **Major Scientific Suppliers (Hong Kong/International)**

1. **Fisher Scientific Hong Kong**
   - Website: fishersci.com.hk
   - Phone: +852 2407 2600
   - Products: Chemicals, lab equipment, consumables
   - Delivery: 1-2 weeks

2. **VWR International (Asia Pacific)**
   - Website: hk.vwr.com
   - Phone: +852 2922 2082
   - Products: Lab equipment, chemicals
   - Delivery: 1-3 weeks

3. **Sigma-Aldrich (Merck) Hong Kong**
   - Website: sigmaaldrich.com/HK/en
   - Phone: +852 2804 5699
   - Products: High-purity chemicals
   - Delivery: 1-2 weeks

### **Electronics Suppliers**

4. **DigiKey Electronics**
   - Website: digikey.com
   - International shipping to Hong Kong
   - Products: HV power supplies, sensors, electronics
   - Delivery: 3-7 days (DHL)

5. **Mouser Electronics**
   - Website: mouser.com
   - International shipping available
   - Products: Power supplies, components
   - Delivery: 3-7 days

6. **RS Components Hong Kong**
   - Website: hk.rs-online.com
   - Phone: +852 2610 3888
   - Products: Test equipment, tools, components
   - Delivery: Next day (local stock)

### **Optics Suppliers**

7. **Edmund Optics (Asia)**
   - Website: edmundoptics.com
   - Email: sales@edmundoptics.com.sg
   - Products: Lenses, cameras, optical components
   - Delivery: 1-2 weeks

8. **Thorlabs**
   - Website: thorlabs.com
   - Ships to Hong Kong
   - Products: Optical mounts, breadboards, cameras
   - Delivery: 1-2 weeks

### **General/Budget Suppliers**

9. **Taobao/Alibaba/AliExpress**
   - Ships to Hong Kong (fast delivery)
   - Products: Low-cost optics, mechanics, electronics
   - Delivery: 1-2 weeks
   - **Note:** Quality varies; order from high-rated sellers

10. **Local Hong Kong Suppliers**
    - **Sham Shui Po Electronics Markets** (深水埗)
      - Address: Apliu Street area
      - Products: Electronics, wire, connectors, tools
      - Cash/immediate pickup
    
    - **Prince Edward Hardware/Tools**
      - Products: Metal sheets, hardware, tools
      - Immediate pickup

---

## Detailed Setup Procedure

### **Phase 1: Pre-Assembly Preparation (1-2 days)**

#### **Step 1.1: Workspace Preparation**

1. **Select appropriate workspace:**
   - Lab bench or sturdy table (minimum 1.2m × 0.8m)
   - Near grounded electrical outlet
   - Good lighting
   - Fire extinguisher accessible (Class C for electrical fires)
   - First aid kit nearby
   - Clear of flammable materials

2. **Verify electrical safety:**
   - Confirm outlet is properly grounded (use outlet tester)
   - Check circuit breaker rating (minimum 10A recommended)
   - Test ground continuity (should read <1Ω to earth)

3. **Organize tools:**
   - Screwdrivers (Phillips and flathead)
   - Allen keys (metric set)
   - Wire strippers and cutters
   - Multimeter
   - Calipers
   - Ruler and measuring tape

#### **Step 1.2: Component Inspection**

1. **Unpack and inventory all components**
2. **Inspect for shipping damage**
3. **Check HV power supply:**
   - Verify voltage/current ratings on label
   - Check for physical damage
   - Test current limiting feature (see safety section)
4. **Test camera:**
   - Connect to computer
   - Verify image capture software works
   - Check lens threading

---

### **Phase 2: Mechanical Assembly (2-3 hours)**

#### **Step 2.1: Enclosure Setup**

1. **Position enclosure on bench:**
   - Leave 30cm clearance on all sides for access
   - Ensure door can open fully
   - Mark locations for cable entry

2. **Install ventilation (if not pre-installed):**
   - Drill holes for air circulation (if using DIY enclosure)
   - Add wire mesh over holes to maintain shielding
   - Do NOT block airflow around HV power supply

3. **Ground the enclosure:**
   - Attach ground wire to metal frame
   - Run to building ground or ground rod
   - Verify continuity: <1Ω to earth ground
   - Label: "SAFETY GROUND - DO NOT REMOVE"

4. **Install interlock switch:**
   - Mount magnetic switch on door frame
   - Wire normally-open contact to HV supply enable line
   - Test: Opening door should cut HV output immediately
   - Label switch: "SAFETY INTERLOCK"

5. **Install emergency stop button:**
   - Mount red mushroom button outside enclosure
   - Wire in series with HV enable
   - Test functionality before proceeding
   - Label: "EMERGENCY STOP"

#### **Step 2.2: Optical Breadboard Assembly**

1. **Mount breadboard inside enclosure:**
   - Use rubber feet or vibration dampers
   - Ensure level (use spirit level)
   - Leave space for HV supply underneath or outside

2. **Install optical posts:**
   - Post 1: Camera mount (rear, centered)
   - Post 2: Needle/syringe holder (front-center)
   - Post 3-4: Electrode mount (front, vertically adjustable)
   - Tighten securely but avoid over-torquing

3. **Attach linear stages:**
   - Stage 1: Mount on post for electrode (vertical adjustment)
   - Stage 2: Mount behind camera for focus adjustment
   - Verify smooth motion, no binding
   - Zero micrometer readings

#### **Step 2.3: Camera and Lens Installation**

1. **Attach lens to camera:**
   - Clean sensor and lens surfaces (use lens cloth)
   - Thread lens onto C-mount (or use adapter)
   - Hand-tighten; do not use tools on threads

2. **Add extension tubes (if using macro lens):**
   - Start with shortest extension (5mm)
   - Can add more for higher magnification
   - Note: More extension = less working distance

3. **Mount camera on post:**
   - Use right-angle clamp
   - Position so lens axis is horizontal
   - Point toward center of breadboard
   - Ensure USB cable can reach outside enclosure

4. **Route camera cable:**
   - Feed USB cable through enclosure opening
   - Leave slack inside for adjustments
   - Secure with cable ties (avoid sharp bends)
   - Connect to computer outside enclosure

#### **Step 2.4: Backlight Setup**

1. **Position LED backlight:**
   - Behind where needle will be (opposite camera)
   - Distance: 15-30cm from needle position
   - Adjust angle for even illumination

2. **Test backlight:**
   - Connect power outside enclosure
   - Verify even illumination (no hot spots)
   - Adjust diffuser if needed

#### **Step 2.5: Needle and Electrode Installation**

1. **Prepare needle holder:**
   - Attach needle to syringe via Luer-Lok
   - Mount syringe in holder clamp
   - Position needle tip at breadboard center
   - Needle should point downward at ~30-45° angle

2. **Prepare extractor electrode:**
   - Polish electrode surface (remove oxidation)
   - Drill small hole for ground wire attachment
   - Attach ground wire with ring terminal and screw
   - Verify continuity to ground

3. **Mount electrode:**
   - Attach to vertical stage
   - Position below needle tip
   - Initial spacing: 20-30mm
   - Verify electrode is level (parallel to needle)

4. **Install spacing measurement:**
   - Use calipers to measure exact needle-to-electrode distance
   - Record initial spacing
   - Mark reference point on stage micrometer

---

### **Phase 3: Electrical Connections (1-2 hours)**

⚠️ **CRITICAL:** All electrical work must be done with HV power supply **UNPLUGGED**

#### **Step 3.1: HV Power Supply Placement**

1. **Position HV supply:**
   - **Outside** enclosure if possible (easier access, better cooling)
   - On rubber mat (electrical insulation)
   - Away from liquids
   - Ventilation unobstructed

2. **Verify all controls are at minimum/off:**
   - Voltage knob: Minimum (fully CCW)
   - Current limit: Minimum
   - Power switch: OFF
   - Main power: UNPLUGGED

#### **Step 3.2: HV Output Connection**

1. **Select appropriate HV cable:**
   - Use HV-rated silicone insulated wire (20-30 kV rating)
   - Length: Minimize excess (2-3m maximum)
   - Color: RED for high voltage
   - Do NOT use standard hookup wire

2. **Connect HV output to needle:**
   - Route HV cable through enclosure grommet
   - Connect to needle holder (must be conductive)
   - Use HV-rated alligator clip or crimp lug
   - Ensure connection is mechanically secure
   - Wrap connection with HV-rated electrical tape
   - Keep cable away from grounded surfaces (>5cm clearance)

3. **Label HV cable:**
   - Attach warning labels every 30cm
   - "HIGH VOLTAGE - DO NOT TOUCH"
   - Include maximum voltage rating

#### **Step 3.3: Ground Connections**

1. **Ground the extractor electrode:**
   - Connect thick ground wire (12 AWG minimum)
   - Run to common ground point
   - Verify continuity to building ground

2. **Ground the enclosure:**
   - Separate ground wire from enclosure frame
   - Connect to same ground point as electrode
   - Verify continuity

3. **Ground the HV supply chassis:**
   - Connect HV supply ground terminal to common ground
   - Verify AC power plug has ground pin
   - DO NOT defeat ground pin

4. **Create single-point ground:**
   - All grounds should connect at ONE point
   - This prevents ground loops
   - Use ground bus bar or large terminal block
   - Final connection to building ground or ground rod

#### **Step 3.4: Interlock Wiring**

1. **Identify HV supply enable/interlock terminals:**
   - Consult manual for your specific supply
   - Usually labeled "INTERLOCK", "ENABLE", or "REMOTE"
   - Typically low voltage (5-24V DC)

2. **Wire interlock circuit:**
   - Connect one wire from enable terminal to door interlock switch
   - Connect second wire from door switch to enable return
   - Circuit must be CLOSED (connected) for HV to operate
   - Opening door breaks circuit, disabling HV

3. **Wire emergency stop in series:**
   - E-stop button in series with door interlock
   - Pressing button breaks circuit immediately
   - Use normally-closed contact on E-stop

4. **Test interlock BEFORE applying HV:**
   - With supply on but voltage at zero:
   - Close door → enable light should turn on
   - Open door → enable light should turn off
   - Press E-stop → enable light should turn off
   - If this doesn't work, DO NOT PROCEED

#### **Step 3.5: Current Limit Verification**

**CRITICAL SAFETY STEP:**

1. **Set current limit to 1 mA:**
   - Adjust current limit pot/knob to minimum
   - Use multimeter in current measurement mode if possible

2. **Verify current limiting:**
   - **Test method (before first HV use):**
     - Connect HV output to 10 MΩ resistor (rated for voltage)
     - Ground other side of resistor
     - Slowly increase voltage
     - At 1 mA: V = I × R = 0.001 A × 10MΩ = 10kV
     - If supply limits current before reaching voltage limit, test passed
     - If supply does NOT limit current, DO NOT USE until fixed

3. **Why 1 mA limit is critical:**
   - Current through human body:
     - >1 mA: Barely perceptible
     - >10 mA: Painful, cannot let go
     - >100 mA: Potentially lethal (ventricular fibrillation)
   - 1 mA limit provides safety margin
   - Still sufficient for Taylor cone formation (nA-µA typical)

---

### **Phase 4: Software and Calibration Setup (1-2 hours)**

#### **Step 4.1: Camera Software Installation**

1. **Install camera drivers:**
   - Download from manufacturer website
   - Install according to instructions
   - Reboot computer if required

2. **Install image capture software:**
   - **Option 1:** Manufacturer software (FLIR Spinnaker, etc.)
   - **Option 2:** OpenCV-based Python script
   - **Option 3:** Free tools: VLC, OBS Studio

3. **Configure camera settings:**
   - Resolution: Maximum (e.g., 2048×1536)
   - Frame rate: 30-60 fps (higher for voltage ramp)
   - Exposure: Manual mode
   - Gain: Start at minimum
   - White balance: Daylight preset

4. **Test image capture:**
   - Verify live view works
   - Test video recording (save to file)
   - Check file format (prefer .avi or .mp4)
   - Verify timestamp is recorded

#### **Step 4.2: Focus and Framing**

1. **Turn on backlight**

2. **Place test object at needle position:**
   - Use printed scale or ruler
   - Position where needle tip will be

3. **Adjust camera focus:**
   - Use live view on computer
   - Adjust lens focus ring or camera position
   - Maximize edge sharpness
   - Use digital zoom to check focus

4. **Adjust framing:**
   - Center needle tip in frame
   - Include area from needle tip to electrode
   - Leave some margin for cone extension
   - Check that lighting is even

5. **Optimize exposure:**
   - Adjust camera exposure time
   - Goal: Needle edge is sharp and dark against bright background
   - Avoid over-saturation (clipping)
   - Histogram should show clear contrast

#### **Step 4.3: Calibration**

1. **Place calibration target in focal plane:**
   - Option A: Precision scale (1951 USAF target)
   - Option B: Ruler with mm markings
   - Position where needle tip will be

2. **Capture calibration image:**
   - Take high-resolution still image
   - Ensure focus is sharp
   - Measure known distance in pixels

3. **Calculate mm/pixel:**
   - Example: 10 mm = 450 pixels → 10/450 = 0.0222 mm/pixel
   - Record this value in metadata file
   - Repeat measurement 3 times, average results

4. **Verify calibration:**
   - Measure needle outer diameter in image
   - Compare to caliper measurement
   - Should agree within 2-3%
   - If not, re-check focus and recalibrate

5. **Lock camera position:**
   - Tighten all clamps securely
   - Mark position with tape (in case of accidental movement)
   - DO NOT adjust focus or camera position after calibration

#### **Step 4.4: Syringe Pump Setup**

1. **Install syringe:**
   - Fill 5 mL syringe with test liquid (water initially)
   - Mount in pump clamp
   - Attach PTFE tubing to syringe Luer connector
   - Secure tubing to prevent kinking

2. **Prime the line:**
   - Run pump at moderate flow rate (10-50 µL/min)
   - Push liquid through tubing until no air bubbles
   - Stop pump once steady drip from needle

3. **Set target flow rate:**
   - Start with 0.5-2 µL/min (very low)
   - This maintains meniscus without excessive flow

4. **Test pump operation:**
   - Verify smooth motion (no jerking)
   - Check for leaks at connections
   - Observe steady drip rate from needle

---

## Safety Protocols and Risk Mitigation

### **Primary Hazards**

1. **Electric shock** (potentially lethal)
2. **High voltage arc/spark** (fire risk)
3. **Chemical exposure** (ethanol, solvents)
4. **Sharp needle** (puncture injury)

---

### **Safety Protocol 1: High Voltage Safety**

#### **Before ANY Experiment:**

✅ **Required checks:**
- [ ] All participants have read and signed safety acknowledgment
- [ ] Supervisor present and briefed on emergency procedures
- [ ] Emergency contact numbers posted on wall
- [ ] Fire extinguisher (Class C) within 3 meters
- [ ] First aid kit accessible
- [ ] Workspace clear of flammable materials
- [ ] All personnel wearing safety glasses
- [ ] Electrical insulating gloves available
- [ ] Door interlock tested and functional
- [ ] Emergency stop button tested
- [ ] All ground connections verified (<1Ω to earth)
- [ ] Current limit verified at 1 mA
- [ ] Only ONE person operates HV controls
- [ ] All observers maintain 2m distance from enclosure

#### **During Experiment:**

✅ **Operating rules:**
- Door MUST be closed before applying HV
- NO adjustments while HV is on
- If adjustment needed: TURN OFF HV → wait 60s → open door → adjust
- Only HV operator touches controls
- All observers stay behind marked line (2m from enclosure)
- Monitor for unusual sounds (buzzing, crackling) → shut down immediately
- Monitor for unusual smells (ozone, burning) → shut down immediately

#### **After Experiment:**

✅ **Shutdown procedure:**
- Turn voltage knob to zero (fully CCW)
- Turn off HV power supply main switch
- Wait minimum 60 seconds (capacitor discharge time)
- Open door (safe to enter)
- Use insulated stick to short HV terminal to ground (extra precaution)
- Only then touch equipment
- Disconnect HV cable from needle
- Cover exposed HV terminals with insulating caps

#### **Emergency: Someone is Being Shocked**

⚠️ **DO NOT TOUCH THE PERSON**

1. **Press emergency stop button** (breaks HV circuit)
2. **If E-stop doesn't work:** Unplug HV power supply
3. **Wait 5 seconds** (let capacitors discharge)
4. **Only then:** Check victim, provide first aid, call emergency services

📞 **Hong Kong Emergency:** 999 (Fire, Ambulance, Police)

---

### **Safety Protocol 2: Chemical Safety**

#### **Ethanol Handling:**

- **Hazard:** Flammable, eye irritant
- **PPE required:** Safety glasses, nitrile gloves, lab coat
- **Ventilation:** Use in well-ventilated area or fume hood
- **Storage:** In flammable-safe cabinet, away from HV equipment
- **Spill cleanup:** Absorb with paper towels, dispose in hazardous waste
- **Disposal:** Follow local hazardous waste regulations (do NOT pour down drain)

#### **Propylene Carbonate Handling:**

- **Hazard:** Eye and skin irritant
- **PPE required:** Safety glasses, nitrile gloves
- **Storage:** Room temperature, sealed container
- **Spill cleanup:** Wipe up, wash area with water
- **Disposal:** Follow local chemical waste regulations

#### **Sodium Chloride (dopant):**

- **Hazard:** Minimal (table salt)
- **Handling:** Wear gloves to avoid contamination
- **Storage:** Sealed container, dry place

#### **First Aid:**

- **Eye contact:** Rinse immediately with water for 15 minutes, seek medical attention
- **Skin contact:** Wash with soap and water
- **Ingestion:** Do not induce vomiting, seek medical attention immediately
- **Inhalation:** Move to fresh air

---

### **Safety Protocol 3: Needle Safety**

- **Hazard:** Sharp point, puncture injury
- **Prevention:**
  - Handle needles by the hub only (never by the shaft)
  - Recap needles when not in use
  - Use blunt-tip needles when possible
  - Secure needles firmly in holder (prevent accidental dislodging)
- **Sharps disposal:**
  - Use designated sharps container
  - Do NOT throw in regular trash
  - Follow local biohazard waste regulations (even though not contaminated)

---

### **Safety Protocol 4: Fire Safety**

#### **Prevention:**
- Keep flammable liquids away from HV sparks (>1m)
- Only store minimum quantity needed for day's experiments
- No open flames in lab
- Check HV cable insulation for damage before each use

#### **Fire Extinguisher Use (Class C):**
- **P.A.S.S. method:**
  - **P**ull the pin
  - **A**im at base of fire
  - **S**queeze the handle
  - **S**weep side to side

- **If fire is electrical:**
  - DO NOT use water
  - Use CO₂ or dry chemical extinguisher
  - Turn off power if safe to do so

- **If fire spreads beyond small area:**
  - Evacuate immediately
  - Close door to contain fire
  - Call 999 (Fire Services)
  - Do NOT re-enter

---

### **Safety Training Requirements**

**Before ANY participant handles equipment:**

1. **Read this entire document**
2. **Watch recommended safety videos:**
   - High voltage electrical safety (YouTube)
   - Chemical handling in labs
   - Fire extinguisher use
3. **Hands-on training session with supervisor:**
   - Practice E-stop procedure
   - Practice capacitor discharge procedure
   - Demonstrate interlock functionality
   - Review first aid kit contents
4. **Sign safety acknowledgment form**
5. **Know emergency contact numbers:**
   - Hong Kong Emergency: 999
   - School emergency contact: _____________
   - Supervisor mobile: _____________

---

## Step-by-Step Experimental Protocol

### **Pre-Experiment Preparation (30 minutes)**

#### **Day Before Experiment:**

1. **Check equipment:**
   - Verify all components are functional
   - Check HV cable insulation (no cracks or damage)
   - Test camera and image capture
   - Verify sufficient liquid supply

2. **Prepare test liquid:**
   - **For ethanol + NaCl:**
     - Measure 100 mL ethanol in graduated cylinder
     - Dissolve 0.01-0.1 g NaCl (adjust for desired conductivity)
     - Stir until fully dissolved
     - Store in sealed bottle, label clearly
     - Record: date, concentration, operator name

3. **Clean equipment:**
   - Wipe down electrode with ethanol (remove residue)
   - Inspect needle for contamination
   - Clean optical surfaces (lens, backlight diffuser)

4. **Prepare metadata template:**
   - Create blank JSON file with all required fields (see paper Section 7)
   - Pre-fill: date, operators, equipment serial numbers

#### **Day of Experiment:**

5. **Complete pre-experiment checklist** (see Safety Protocol 1)

6. **Brief all participants:**
   - Review roles (who operates HV, who records data, who observes)
   - Review E-stop location and procedure
   - Confirm everyone has read safety protocols

---

### **Experiment Setup (15-20 minutes)**

7. **Install fresh needle:**
   - Attach needle to filled syringe (test liquid)
   - Mount in holder
   - Prime line: run pump until steady drip, then stop

8. **Set electrode spacing:**
   - Use calipers to measure distance
   - Start with L = 20 mm
   - Record exact spacing in metadata

9. **Position camera:**
   - Verify framing (needle tip centered)
   - Check focus (should not have changed from calibration)
   - Adjust lighting if needed

10. **Start image recording:**
    - Begin video capture
    - Display timestamp overlay if possible
    - Verify recording is active (file size increasing)

---

### **Voltage Ramp Protocol (30-60 minutes)**

11. **Initial state:**
    - Voltage: 0 V
    - Pump: OFF
    - Camera: Recording
    - Note starting timestamp

12. **Start liquid flow:**
    - Set pump to 0.5-2 µL/min
    - Observe meniscus forming at needle tip
    - Wait until steady hemispherical droplet appears (~1-2 min)
    - If droplet falls: reduce flow rate
    - Record stable flow rate in metadata

13. **Close enclosure and enable HV:**
    - Close door (verify interlock engages)
    - Turn on HV power supply main switch
    - Verify enable LED is lit
    - Voltage should still be at zero

14. **Begin voltage sweep:**
    - **Step size:** 100-200 V per step
    - **Dwell time:** 20-30 seconds per step
    - **Procedure for each step:**
      1. Increase voltage by one step
      2. Read voltage display, announce/record value
      3. Observe meniscus through camera feed
      4. Classify state:
         - "Hemispherical" - no deformation
         - "Ellipsoidal" - slight elongation
         - "Conical-unstable" - cone forms but oscillates
         - "Conical-stable" - steady cone, no spray
         - "Spray" - visible jet/droplet emission
      5. Make verbal annotation (recorded by camera audio)
      6. Wait for full dwell time before next step

15. **Identify onset condition:**
    - **Onset voltage (V₀):** First voltage where stable cone appears
    - Hold at this voltage for 60 seconds
    - Verify stability (no jetting, no collapse)
    - Record voltage and timestamp

16. **Continue voltage sweep (optional):**
    - Increase to 1-2 steps beyond onset
    - Observe transition to spray
    - **STOP immediately if:**
      - Sparking/arcing occurs → shut down, investigate
      - Unusual odor → shut down, ventilate
      - Current meter shows >1 mA → shut down, check connections

17. **Voltage ramp down:**
    - Decrease voltage in same-size steps
    - Return to 0 V
    - Observe if cone persists at lower voltages (hysteresis)
    - Record any hysteresis behavior

18. **Repeat trial:**
    - With voltage at zero, wait 1-2 minutes
    - Repeat steps 14-17 (second trial)
    - Perform minimum 3 trials for repeatability

---

### **Shutdown Procedure (10 minutes)**

19. **Power down:**
    - Turn voltage to zero
    - Turn off HV power supply
    - Wait 60 seconds
    - Stop syringe pump
    - Stop video recording

20. **Safe equipment access:**
    - Open enclosure door
    - Short HV terminal to ground (insulated stick)
    - Disconnect HV cable from needle
    - Remove test liquid syringe

21. **Clean up:**
    - Wipe any liquid residue from electrode
    - Dispose of used needle in sharps container
    - Cap and label used liquid (if reusing)
    - Store liquids in flammable cabinet

22. **Data backup:**
    - Copy video files to backup drive
    - Verify file integrity (can play back)
    - Fill in metadata template
    - Save metadata as JSON file with same filename as video

---

### **Post-Experiment Analysis**

23. **Frame selection:**
    - Review video for stable cone periods
    - Extract frames at onset voltage (steady-state region)
    - Save frames as individual image files

24. **Image processing:**
    - Run computer vision pipeline (Section 8 of paper)
    - Extract cone profile coordinates
    - Measure half-angle
    - Calculate uncertainties

25. **Comparison with simulation:**
    - Run solver with same parameters (L, γ, V₀)
    - Extract simulated cone angle
    - Compare: Δα = α_exp - α_sim
    - Compute profile RMSE

26. **Fill results tables:**
    - Update Section 9 placeholder tables
    - Include uncertainties
    - Note any anomalies or issues

---

## Troubleshooting Guide

### **Problem 1: No meniscus forms at needle tip**

**Possible causes:**
- Flow rate too low
- Needle clogged
- Liquid wetting properties poor

**Solutions:**
- Increase flow rate gradually (0.5 → 1 → 2 µL/min)
- Check for blockage: disconnect needle, run pump, verify flow
- Replace needle if clogged
- Check liquid surface tension (should be >20 mN/m for stable meniscus)

---

### **Problem 2: Meniscus oscillates or drips**

**Possible causes:**
- Flow rate too high
- Vibrations in setup
- Poor needle attachment

**Solutions:**
- Reduce flow rate
- Check if pump is vibrating → isolate with rubber pad
- Tighten needle connection to syringe
- Ensure breadboard is stable and level

---

### **Problem 3: No cone formation even at high voltage**

**Possible causes:**
- Liquid not conductive enough
- Electrode spacing too large
- Voltage too low
- Poor electrical connection

**Solutions:**
- Increase dopant concentration (add more NaCl)
- Measure liquid conductivity (should be >10 µS/cm)
- Reduce electrode spacing to 10-15 mm
- Check HV connection to needle (verify continuity)
- Increase voltage gradually (literature onset: 2-5 kV typical)

---

### **Problem 4: Immediate spray/jetting (no stable cone)**

**Possible causes:**
- Flow rate too high
- Voltage increased too quickly
- Liquid too conductive

**Solutions:**
- Reduce flow rate to minimum (<0.5 µL/min)
- Increase voltage more gradually (50V steps instead of 100V)
- Reduce dopant concentration (dilute liquid)

---

### **Problem 5: Sparking/arcing between needle and electrode**

**Possible causes:**
- Voltage too high for given spacing
- Sharp edges on electrode
- Contamination on surfaces

**Solutions:**
- **Immediately reduce voltage to zero**
- Increase electrode spacing
- Polish electrode edges (remove burrs)
- Clean surfaces with ethanol
- Check for conductive debris (liquid droplets on surfaces)

---

### **Problem 6: Blurry images / poor contrast**

**Possible causes:**
- Camera out of focus
- Backlight too dim or too bright
- Condensation on optics

**Solutions:**
- Re-focus camera (use printed scale at needle position)
- Adjust backlight brightness
- Adjust camera exposure time
- Check for condensation on lens (wipe with lens cloth)
- Ensure needle is in focal plane (didn't move during setup)

---

### **Problem 7: Current limit triggers immediately**

**Possible causes:**
- Short circuit somewhere
- Liquid dripping onto electrode
- Current limit set too low

**Solutions:**
- **Turn off HV immediately**
- Check for liquid bridge between needle and electrode
- Inspect HV cable for damage (shorts to ground)
- Verify current limit is set correctly (1 mA)
- Dry all surfaces thoroughly before retry

---

## Emergency Procedures

### **Emergency 1: Electrical Shock**

**If someone is being shocked:**
1. **DO NOT TOUCH THE PERSON**
2. Press emergency stop button or unplug HV supply
3. Wait 5 seconds
4. Check victim:
   - Conscious? → Reassure, check for burns, seek medical attention
   - Unconscious? → Call 999 immediately, begin CPR if trained
5. Do not move victim unless necessary for safety

**Minor shock (tingling, no injury):**
- Report to supervisor
- Document incident
- Review safety procedures before continuing

---

### **Emergency 2: Fire**

**Small fire (< 30 cm):**
1. Press emergency stop (cut power)
2. Use fire extinguisher (Class C)
3. Aim at base of fire, sweep side to side
4. If extinguished: ventilate area, document incident
5. If spreads: proceed to large fire procedure

**Large fire or spreading rapidly:**
1. Evacuate immediately (do not stop for belongings)
2. Close door to lab
3. Pull fire alarm
4. Call 999 from safe location
5. Meet at designated assembly point
6. Do NOT re-enter building

---

### **Emergency 3: Chemical Spill**

**Small spill (< 100 mL):**
1. Alert others in area
2. Put on gloves and safety glasses
3. Absorb with paper towels or spill kit absorbent
4. Dispose in chemical waste container
5. Wipe area with water
6. Ventilate area

**Large spill (> 100 mL):**
1. Evacuate area
2. Close door to contain vapors
3. Alert supervisor/building management
4. Follow institutional spill response procedures

**Spill on person:**
- Remove contaminated clothing immediately
- Rinse affected area with water for 15 minutes
- Seek medical attention if irritation persists

---

### **Emergency 4: Eye Injury**

**Chemical splash to eye:**
1. Immediately flush eye with water for 15 minutes
2. Use eyewash station if available
3. Hold eyelids open during flushing
4. Call 999 / seek medical attention immediately
5. Bring MSDS or chemical information to hospital

**Foreign object in eye:**
- Do NOT rub eye
- Flush gently with water
- If object remains: seek medical attention
- Do NOT attempt to remove embedded objects

---

### **Emergency 5: Equipment Malfunction**

**Smoke from HV power supply:**
1. Turn off power immediately
2. Unplug from wall
3. Evacuate if smoke persists
4. Do NOT attempt repairs
5. Contact manufacturer/qualified technician

**Burning smell:**
1. Turn off power
2. Identify source (sniff carefully, don't inhale deeply)
3. If electrical: unplug device
4. If chemical: ventilate area, identify spill
5. Do NOT restart equipment until cause identified

---

## Pre-Experiment Safety Checklist

**Print and complete before EVERY experiment session:**

---

**Date:** ________________  
**Operators:** ______________________, ______________________, ______________________  
**Supervisor:** ______________________  
**Start time:** ____________

### **Equipment Checks**

- [ ] HV power supply: voltage at zero, current limit at 1 mA
- [ ] Interlock switch: tested and functional (open door → HV disables)
- [ ] Emergency stop: tested and functional (press button → HV disables)
- [ ] Ground connections: verified <1Ω to earth
- [ ] HV cable: inspected for damage (no cracks, no exposed conductor)
- [ ] Enclosure: door closes properly, no gaps
- [ ] Camera: recording function tested
- [ ] Backlight: functional, no flickering
- [ ] Syringe pump: smooth operation, no leaks
- [ ] Liquid supply: sufficient for planned experiments, properly labeled

### **Safety Equipment**

- [ ] Fire extinguisher: present, charged, within 3 meters
- [ ] First aid kit: present and accessible
- [ ] Safety glasses: all participants wearing
- [ ] Electrical insulating gloves: available at workstation
- [ ] Nitrile gloves: available
- [ ] Lab coats: all participants wearing

### **Workspace**

- [ ] Area cleared of flammable materials (>1m from enclosure)
- [ ] Emergency contact numbers posted on wall
- [ ] Adequate ventilation (windows open or fume hood on)
- [ ] Clear path to exit (no obstructions)
- [ ] Observers maintain 2m distance (marked line on floor)

### **Personnel**

- [ ] All participants have read safety protocols
- [ ] All participants have signed safety acknowledgment
- [ ] Roles assigned (HV operator: _______, recorder: _______, observer: _______)
- [ ] Everyone knows location of E-stop and fire extinguisher
- [ ] Everyone knows emergency phone number: 999

### **Final Checks**

- [ ] Supervisor present and briefed
- [ ] Mobile phone present (for emergency calls)
- [ ] No food or drinks in work area
- [ ] No loose clothing or jewelry near moving parts

---

**Supervisor signature:** ______________________  
**Approval to proceed:** YES / NO

---

## Acknowledgment of Safety Training

**I, _________________________________ (print name), acknowledge that:**

1. I have read and understood this entire safety document
2. I have been trained on the location and use of:
   - Emergency stop button
   - Fire extinguisher
   - First aid kit
   - Eyewash station (if available)
3. I understand the hazards of high voltage electricity
4. I know that:
   - Current >10 mA can cause inability to let go
   - Current >100 mA can be lethal
   - Voltage is not the danger; current through the body is
5. I will follow all safety protocols without exception
6. I will immediately report any unsafe conditions to the supervisor
7. I will not operate equipment without supervisor present
8. I will not defeat or bypass any safety interlocks
9. I understand that violations of safety protocols will result in immediate removal from the project

**Signature:** ______________________  
**Date:** ____________  
**Supervisor signature:** ______________________  
**Date:** ____________

---

## Appendix A: Quick Reference - Onset Voltage Estimation

Use this to predict expected onset voltage for your geometry:

**Simplified onset voltage formula:**
$$V_0 \approx \sqrt{\frac{4\gamma L}{\varepsilon_0 \ln(4L/r_{\text{needle}})}}$$

Where:
- γ = surface tension (N/m)
- L = electrode spacing (m)
- ε₀ = 8.854×10⁻¹² F/m
- r_needle = needle outer radius (m)

**Example calculation (ethanol, 21-gauge needle, 20mm spacing):**
- γ = 0.022 N/m (ethanol)
- L = 0.020 m
- r_needle = 0.0004 m (21-gauge OD = 0.8 mm)
- ln(4×0.020/0.0004) = ln(200) ≈ 5.3

$$V_0 \approx \sqrt{\frac{4 \times 0.022 \times 0.020}{8.854 \times 10^{-12} \times 5.3}}$$
$$V_0 \approx \sqrt{\frac{0.00176}{4.69 \times 10^{-11}}}$$
$$V_0 \approx \sqrt{3.75 \times 10^7}$$
$$V_0 \approx 6,100 \text{ V}$$

**Expect onset around 6 kV for this geometry.**

**If your estimation is >10 kV:**
- Reduce electrode spacing (try L = 10-15 mm)
- Use larger needle (18-gauge instead of 21-gauge)

---

## Appendix B: Metadata Template (JSON)

Save this template and fill for each trial:

```json
{
  "trial_id": "TRIAL_001",
  "date": "2026-08-20",
  "time_start": "14:30:00",
  "operator": "Ethan Yang",
  "supervisor": "Dr. [Name]",
  "session_notes": "",
  
  "geometry": {
    "electrode_spacing_mm": 20.0,
    "needle_outer_diameter_mm": 0.80,
    "needle_inner_diameter_mm": 0.51,
    "needle_gauge": 21,
    "extractor_geometry": "plate",
    "extractor_dimensions_mm": "50x50x1"
  },
  
  "liquid": {
    "name": "Ethanol (190 proof)",
    "purity": "95%",
    "supplier": "Fisher Scientific",
    "surface_tension_N_per_m": 0.022,
    "conductivity_S_per_m": 1.5e-4,
    "dopant_identity": "NaCl",
    "dopant_concentration_g_per_L": 0.1,
    "temperature_C": 22
  },
  
  "operation": {
    "flow_rate_uL_per_min": 1.0,
    "voltage_step_V": 100,
    "dwell_time_s": 20,
    "voltage_ramp_start_V": 0,
    "voltage_ramp_end_V": 7000,
    "onset_voltage_V": 6200
  },
  
  "imaging": {
    "camera_model": "FLIR Blackfly S",
    "resolution_px": [2048, 1536],
    "frame_rate_fps": 30,
    "lens_focal_length_mm": 25,
    "lens_type": "C-mount macro",
    "working_distance_mm": 150,
    "calibration_mm_per_px": 0.0222,
    "backlight": "Huion LED pad",
    "exposure_ms": 5.0,
    "gain_dB": 0
  },
  
  "environment": {
    "ambient_temp_C": 22,
    "ambient_humidity_percent": 60,
    "location": "ISF Academy Physics Lab"
  },
  
  "files": {
    "video": "TRIAL_001_video.avi",
    "calibration_image": "TRIAL_001_calibration.png",
    "metadata": "TRIAL_001_metadata.json"
  }
}
```

---

## Appendix C: Supplier Contact Information (Hong Kong)

**Fisher Scientific Hong Kong**
- Address: Units 604-605, 6/F, Tower 1, Grand Central Plaza, 138 Shatin Rural Committee Road, Shatin, Hong Kong
- Phone: +852 2407 2600
- Email: info.hk@thermofisher.com
- Website: fishersci.com.hk

**VWR International Asia Pacific**
- Phone: +852 2922 2082
- Email: sales_hk@vwr.com
- Website: hk.vwr.com

**RS Components Hong Kong**
- Address: 18/F, Tower A, Billion Centre, 1 Wang Kwong Road, Kowloon Bay
- Phone: +852 2610 3888
- Website: hk.rs-online.com

**Sham Shui Po Electronics Market**
- Location: Apliu Street (鴨寮街), Sham Shui Po
- MTR: Sham Shui Po Station Exit C2
- Hours: Daily 10:00-20:00
- Best for: Cables, connectors, tools, basic electronics

---

## Document Version Control

**Version:** 1.0  
**Date:** August 20, 2026  
**Authors:** Ethan Yang, Elliot Dong, Curtis Lau  
**Reviewed by:** [Supervisor name]  
**Approval date:** ______________

**Revision History:**
- v1.0 (2026-08-20): Initial document creation

---

**END OF DOCUMENT**

**Total pages:** 41  
**Estimated read time:** 2-3 hours  
**Estimated setup time:** 2-3 days (including parts procurement)  
**Estimated cost:** $1,500-9,000 USD depending on equipment choice
