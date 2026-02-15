# FINDEM – Fauna Invasion Detection & Elimination Mechanism
## System Requirements Document

**Version:** 1.0  
**Date:** February 15, 2026  
**Project Type:** Offline Edge-AI Animal Deterrence System

---

## 1. Introduction

### 1.1 Purpose
This document specifies the system requirements for FINDEM (Fauna Invasion Detection & Elimination Mechanism), an offline edge-AI system designed to detect and deter wild animals from agricultural farmland.

### 1.2 Scope
FINDEM is a standalone, battery-powered system that operates without internet connectivity, cloud services, or mobile applications. The system uses computer vision and audio deterrence to protect crops from animal intrusion.

### 1.3 Document Conventions
- **SHALL**: Mandatory requirement
- **SHOULD**: Recommended requirement
- **MAY**: Optional requirement

---

## 2. System Overview

### 2.1 System Description
FINDEM is a rugged, edge-deployed system that performs on-device AI training and real-time animal detection. The system captures images, trains a local YOLO model through data augmentation and image blending, and activates audio deterrents when target animals are detected.

### 2.2 Target Animals
- Elephants
- Wild boars
- Monkeys
- Deer

### 2.3 System Components
- Central processing unit: NVIDIA Jetson Nano 2GB
- Up to 3 wired cameras
- 1-2 wired PA horn speakers
- Battery power system
- Physical numeric keypad
- Physical start button
- LED indicators (Red, Yellow, Green)

### 2.4 Operating Mode
- Fully offline operation
- No network connectivity (internet, WiFi, cellular)
- No graphical user interface
- Physical interaction only (buttons and LEDs)

---

## 3. Stakeholders and Users

### 3.1 Primary Users
- **Farmers**: Agricultural workers responsible for crop protection
- **Farm operators**: Personnel managing farm equipment and systems

### 3.2 User Characteristics
- Limited technical expertise
- Familiarity with basic farm equipment
- May have limited literacy or language skills
- Require simple, intuitive physical interfaces

### 3.3 Secondary Stakeholders
- System installers and maintenance technicians
- Agricultural equipment suppliers
- Wildlife management authorities

---

## 4. Assumptions and Constraints

### 4.1 Assumptions
- Cameras have clear line of sight to farm perimeter or entry points
- Sufficient ambient or infrared lighting for image capture
- Animals exhibit deterrence response to audio stimuli
- Battery system provides adequate power for 24/7 operation
- Training images of target animals are available or can be captured

### 4.2 Constraints
- **Hardware**: Limited to Jetson Nano 2GB computational capacity
- **Memory**: 2GB RAM constraint for model training and inference
- **Storage**: Limited local storage for images and model weights
- **Power**: Battery-dependent operation with no grid connection
- **Connectivity**: Zero network connectivity
- **Interface**: No screen or graphical display
- **Environmental**: Outdoor deployment in agricultural conditions

---

## 5. Functional Requirements

### 5.1 Training Requirements

#### 5.1.1 Image Capture
- **REQ-TR-001**: System SHALL capture images from connected cameras on demand
- **REQ-TR-002**: System SHALL support simultaneous capture from up to 3 cameras
- **REQ-TR-003**: System SHALL store captured images locally
- **REQ-TR-004**: System SHALL associate captured images with animal class labels via keypad input

#### 5.1.2 Data Augmentation
- **REQ-TR-005**: System SHALL perform data augmentation on captured images
- **REQ-TR-006**: Augmentation techniques SHALL include:
  - Rotation
  - Scaling
  - Brightness adjustment
  - Horizontal flipping
  - Noise injection
- **REQ-TR-007**: System SHALL generate multiple augmented variants per source image

#### 5.1.3 Image Blending
- **REQ-TR-008**: System SHALL blend animal images onto farm background images
- **REQ-TR-009**: Blending SHALL create realistic composite training images
- **REQ-TR-010**: System SHALL randomize animal position, scale, and orientation during blending
- **REQ-TR-011**: System SHALL maintain aspect ratio and natural appearance of blended animals

#### 5.1.4 Model Training
- **REQ-TR-012**: System SHALL train a YOLO object detection model locally on Jetson Nano
- **REQ-TR-013**: Training SHALL use augmented and blended image dataset
- **REQ-TR-014**: System SHALL support training for multiple animal classes simultaneously
- **REQ-TR-015**: System SHALL indicate training progress via LED status
- **REQ-TR-016**: System SHALL save trained model weights to local storage
- **REQ-TR-017**: Training process SHALL complete within reasonable time given hardware constraints (target: <24 hours)
- **REQ-TR-018**: System SHALL allow training to be initiated via physical start button

### 5.2 Detection Requirements

#### 5.2.1 Real-Time Inference
- **REQ-DT-001**: System SHALL perform real-time object detection on camera feeds
- **REQ-DT-002**: System SHALL process frames from all connected cameras
- **REQ-DT-003**: Detection latency SHALL be minimized for rapid response (target: <2 seconds)
- **REQ-DT-004**: System SHALL identify animal class (elephant, boar, monkey, deer)
- **REQ-DT-005**: System SHALL calculate confidence score for each detection

#### 5.2.2 Detection Thresholds
- **REQ-DT-006**: System SHALL use configurable confidence threshold for positive detection
- **REQ-DT-007**: Default confidence threshold SHALL be set to minimize false positives
- **REQ-DT-008**: System SHALL ignore detections below confidence threshold

#### 5.2.3 Detection Persistence
- **REQ-DT-009**: System SHALL log detection events locally
- **REQ-DT-010**: Detection logs SHALL include timestamp, animal class, confidence, and camera ID
- **REQ-DT-011**: System SHALL maintain detection history within storage constraints

### 5.3 Audio Deterrence Requirements

#### 5.3.1 Audio Activation
- **REQ-AD-001**: System SHALL activate audio deterrent when animal is detected
- **REQ-AD-002**: Audio activation SHALL occur within 2 seconds of detection
- **REQ-AD-003**: System SHALL support 1-2 wired PA horn speakers
- **REQ-AD-004**: System SHALL route audio to all connected speakers simultaneously

#### 5.3.2 Audio Randomization
- **REQ-AD-005**: System SHALL randomize audio deterrent selection
- **REQ-AD-006**: System SHALL maintain library of deterrent audio files
- **REQ-AD-007**: Randomization SHALL prevent animal habituation to specific sounds
- **REQ-AD-008**: System SHALL support different audio profiles per animal class

#### 5.3.3 Audio Control
- **REQ-AD-009**: System SHALL allow audio volume configuration
- **REQ-AD-010**: System SHALL limit audio duration to prevent excessive noise
- **REQ-AD-011**: System SHALL implement cooldown period between audio activations
- **REQ-AD-012**: System SHALL allow manual audio test via keypad command

### 5.4 User Interaction Requirements

#### 5.4.1 Physical Controls
- **REQ-UI-001**: System SHALL provide numeric keypad for user input
- **REQ-UI-002**: System SHALL provide dedicated start button for training initiation
- **REQ-UI-003**: Keypad SHALL support command entry for system configuration
- **REQ-UI-004**: System SHALL provide tactile feedback for button presses

#### 5.4.2 LED Indicators
- **REQ-UI-005**: System SHALL provide three LED indicators: Red, Yellow, Green
- **REQ-UI-006**: Green LED SHALL indicate normal operation/detection active
- **REQ-UI-007**: Yellow LED SHALL indicate training in progress
- **REQ-UI-008**: Red LED SHALL indicate system error or fault condition
- **REQ-UI-009**: LED patterns SHALL communicate system state clearly
- **REQ-UI-010**: System SHALL support LED blinking patterns for additional status information

#### 5.4.3 Mode Selection
- **REQ-UI-011**: System SHALL support training mode and detection mode
- **REQ-UI-012**: Mode switching SHALL be performed via keypad command
- **REQ-UI-013**: System SHALL prevent mode switching during active operations
- **REQ-UI-014**: Current mode SHALL be indicated via LED status

#### 5.4.4 Configuration
- **REQ-UI-015**: System SHALL allow configuration of detection sensitivity via keypad
- **REQ-UI-016**: System SHALL allow configuration of audio volume via keypad
- **REQ-UI-017**: System SHALL persist configuration settings across power cycles
- **REQ-UI-018**: System SHALL provide factory reset capability via keypad sequence

---

## 6. Non-Functional Requirements

### 6.1 Performance

#### 6.1.1 Processing Performance
- **REQ-NF-001**: Detection inference SHALL achieve minimum 5 FPS on Jetson Nano 2GB
- **REQ-NF-002**: System SHALL process multiple camera feeds concurrently
- **REQ-NF-003**: Memory usage SHALL not exceed 1.8GB during normal operation
- **REQ-NF-004**: Model training SHALL complete within 24 hours for typical dataset size

#### 6.1.2 Response Time
- **REQ-NF-005**: System startup time SHALL be less than 60 seconds
- **REQ-NF-006**: Detection-to-deterrent latency SHALL be less than 2 seconds
- **REQ-NF-007**: User input response time SHALL be less than 500ms

### 6.2 Reliability

#### 6.2.1 Availability
- **REQ-NF-008**: System SHALL operate continuously 24/7
- **REQ-NF-009**: System SHALL recover automatically from transient faults
- **REQ-NF-010**: System uptime SHALL exceed 99% under normal conditions

#### 6.2.2 Fault Tolerance
- **REQ-NF-011**: System SHALL continue operation if one camera fails
- **REQ-NF-012**: System SHALL continue operation if one speaker fails
- **REQ-NF-013**: System SHALL detect and report hardware failures via LED indicators
- **REQ-NF-014**: System SHALL implement watchdog timer for automatic recovery

#### 6.2.3 Data Integrity
- **REQ-NF-015**: System SHALL protect stored data from corruption
- **REQ-NF-016**: System SHALL validate model weights before loading
- **REQ-NF-017**: System SHALL maintain configuration integrity across power cycles

### 6.3 Usability

#### 6.3.1 Ease of Use
- **REQ-NF-018**: System operation SHALL require minimal training for farmers
- **REQ-NF-019**: LED indicators SHALL provide clear, unambiguous status information
- **REQ-NF-020**: Keypad commands SHALL follow simple, memorable patterns
- **REQ-NF-021**: System SHALL provide audio feedback for critical operations

#### 6.3.2 Documentation
- **REQ-NF-022**: System SHALL include printed quick-start guide
- **REQ-NF-023**: Documentation SHALL use simple language and diagrams
- **REQ-NF-024**: LED status codes SHALL be documented on device label

### 6.4 Maintainability

#### 6.4.1 Serviceability
- **REQ-NF-025**: System SHALL support field replacement of cameras and speakers
- **REQ-NF-026**: System SHALL support battery replacement without data loss
- **REQ-NF-027**: System SHALL log error conditions for troubleshooting
- **REQ-NF-028**: System SHALL provide diagnostic mode accessible via keypad

#### 6.4.2 Software Updates
- **REQ-NF-029**: System SHALL support model updates via local storage media (USB)
- **REQ-NF-030**: System SHALL support firmware updates via local storage media
- **REQ-NF-031**: Update process SHALL not require internet connectivity

### 6.5 Safety

#### 6.5.1 Electrical Safety
- **REQ-NF-032**: System SHALL comply with electrical safety standards for outdoor equipment
- **REQ-NF-033**: System SHALL include overcurrent protection
- **REQ-NF-034**: System SHALL include short-circuit protection

#### 6.5.2 Audio Safety
- **REQ-NF-035**: Audio output SHALL not exceed safe sound pressure levels for humans
- **REQ-NF-036**: System SHALL include audio limiter to prevent speaker damage
- **REQ-NF-037**: System SHALL provide warning label for audio hazard

#### 6.5.3 Wildlife Safety
- **REQ-NF-038**: Deterrence methods SHALL be non-lethal
- **REQ-NF-039**: Audio frequencies SHALL be selected to minimize harm to animals

---

## 7. Hardware Requirements

### 7.1 Processing Unit
- **REQ-HW-001**: Central processor: NVIDIA Jetson Nano 2GB
- **REQ-HW-002**: GPU: 128-core Maxwell GPU
- **REQ-HW-003**: RAM: 2GB LPDDR4
- **REQ-HW-004**: Storage: Minimum 64GB SD card or eMMC

### 7.2 Cameras
- **REQ-HW-005**: Camera interface: CSI or USB
- **REQ-HW-006**: Camera resolution: Minimum 1080p
- **REQ-HW-007**: Camera count: Support for up to 3 cameras
- **REQ-HW-008**: Camera connection: Wired only
- **REQ-HW-009**: Night vision: IR capability recommended

### 7.3 Audio System
- **REQ-HW-010**: Speaker type: PA horn speakers
- **REQ-HW-011**: Speaker count: 1-2 units
- **REQ-HW-012**: Speaker connection: Wired only
- **REQ-HW-013**: Audio output: Minimum 100W per speaker
- **REQ-HW-014**: Audio interface: Analog or USB audio adapter

### 7.4 User Interface Hardware
- **REQ-HW-015**: Numeric keypad: 0-9 keys plus function keys
- **REQ-HW-016**: Start button: Momentary push button
- **REQ-HW-017**: LED indicators: Red, Yellow, Green (high-brightness)
- **REQ-HW-018**: Interface connection: GPIO or USB

### 7.5 Power System
- **REQ-HW-019**: Battery type: Deep-cycle lead-acid or lithium-ion
- **REQ-HW-020**: Battery capacity: Minimum 100Ah for 24-hour operation
- **REQ-HW-021**: Solar charging: Optional solar panel integration
- **REQ-HW-022**: Power management: Low-voltage cutoff protection

### 7.6 Enclosure
- **REQ-HW-023**: Enclosure rating: IP65 or higher
- **REQ-HW-024**: Material: UV-resistant, weatherproof
- **REQ-HW-025**: Mounting: Pole or wall mount capability
- **REQ-HW-026**: Ventilation: Passive cooling for Jetson Nano

---

## 8. Software Requirements

### 8.1 Operating System
- **REQ-SW-001**: OS: Linux-based (Ubuntu 18.04 or JetPack SDK)
- **REQ-SW-002**: Kernel: ARM64 compatible
- **REQ-SW-003**: Boot: Automatic startup on power-on

### 8.2 AI Framework
- **REQ-SW-004**: Deep learning framework: TensorFlow, PyTorch, or TensorRT
- **REQ-SW-005**: Object detection: YOLO (v5, v7, or v8)
- **REQ-SW-006**: Model format: Optimized for Jetson inference (TensorRT)

### 8.3 Computer Vision
- **REQ-SW-007**: Image processing: OpenCV or equivalent
- **REQ-SW-008**: Camera interface: GStreamer or V4L2
- **REQ-SW-009**: Image augmentation: Albumentations or imgaug

### 8.4 Audio Processing
- **REQ-SW-010**: Audio playback: ALSA or PulseAudio
- **REQ-SW-011**: Audio format support: WAV, MP3
- **REQ-SW-012**: Audio mixing: Support for randomized playback

### 8.5 System Software
- **REQ-SW-013**: Hardware interface: GPIO library (e.g., Jetson.GPIO)
- **REQ-SW-014**: Data persistence: SQLite or file-based storage
- **REQ-SW-015**: Logging: Structured logging with rotation
- **REQ-SW-016**: Watchdog: System monitoring and auto-restart

### 8.6 Application Software
- **REQ-SW-017**: Main application: Python or C++ based
- **REQ-SW-018**: State machine: Training mode, detection mode, configuration mode
- **REQ-SW-019**: Configuration: File-based or embedded database
- **REQ-SW-020**: Error handling: Graceful degradation and recovery

---

## 9. Environmental Requirements

### 9.1 Operating Environment
- **REQ-ENV-001**: Operating temperature: -10°C to 50°C
- **REQ-ENV-002**: Storage temperature: -20°C to 60°C
- **REQ-ENV-003**: Humidity: 0-95% non-condensing
- **REQ-ENV-004**: Ingress protection: IP65 minimum

### 9.2 Physical Environment
- **REQ-ENV-005**: Deployment: Outdoor agricultural setting
- **REQ-ENV-006**: Exposure: Direct sunlight, rain, dust
- **REQ-ENV-007**: Vibration: Resistant to wind and animal contact
- **REQ-ENV-008**: Altitude: 0-2000m above sea level

### 9.3 Electromagnetic Environment
- **REQ-ENV-009**: EMI: Resistant to agricultural equipment interference
- **REQ-ENV-010**: Lightning: Surge protection recommended
- **REQ-ENV-011**: Static discharge: ESD protection on exposed interfaces

---

## 10. Power and Energy Requirements

### 10.1 Power Consumption
- **REQ-PWR-001**: Jetson Nano: Maximum 10W
- **REQ-PWR-002**: Cameras: Maximum 5W per camera (15W total)
- **REQ-PWR-003**: Speakers: Maximum 200W during activation
- **REQ-PWR-004**: Peripherals: Maximum 5W (keypad, LEDs)
- **REQ-PWR-005**: Total continuous: Maximum 30W (excluding speakers)

### 10.2 Battery Life
- **REQ-PWR-006**: Continuous operation: Minimum 24 hours on battery
- **REQ-PWR-007**: Detection mode: Minimum 48 hours without audio activation
- **REQ-PWR-008**: Low-power mode: Optional sleep mode during daylight hours

### 10.3 Charging
- **REQ-PWR-009**: Charging method: Solar panel or AC adapter
- **REQ-PWR-010**: Charge time: Full charge within 8 hours of sunlight
- **REQ-PWR-011**: Charge controller: MPPT for solar efficiency

### 10.4 Power Management
- **REQ-PWR-012**: Low battery warning: LED indication at 20% capacity
- **REQ-PWR-013**: Critical battery: Graceful shutdown at 5% capacity
- **REQ-PWR-014**: Power monitoring: Battery voltage and current logging

---

## 11. Operational Requirements

### 11.1 Installation
- **REQ-OPS-001**: Installation time: Less than 2 hours
- **REQ-OPS-002**: Tools required: Basic hand tools only
- **REQ-OPS-003**: Calibration: Camera positioning and audio testing
- **REQ-OPS-004**: Initial setup: Factory default configuration

### 11.2 Training Workflow
- **REQ-OPS-005**: Image collection: Capture 50-200 images per animal class
- **REQ-OPS-006**: Labeling: Keypad-based class assignment
- **REQ-OPS-007**: Training initiation: Single button press
- **REQ-OPS-008**: Training duration: 12-24 hours typical

### 11.3 Detection Workflow
- **REQ-OPS-009**: Activation: Automatic on system startup
- **REQ-OPS-010**: Monitoring: Continuous 24/7 operation
- **REQ-OPS-011**: Intervention: Automatic audio deterrence
- **REQ-OPS-012**: Logging: Passive event recording

### 11.4 Maintenance
- **REQ-OPS-013**: Routine maintenance: Monthly inspection
- **REQ-OPS-014**: Camera cleaning: As needed for image quality
- **REQ-OPS-015**: Battery maintenance: Quarterly capacity check
- **REQ-OPS-016**: Model retraining: Seasonal or as needed

---

## 12. Limitations and Risks

### 12.1 Technical Limitations
- **LIM-001**: Detection accuracy limited by Jetson Nano 2GB computational capacity
- **LIM-002**: Training dataset size constrained by local storage
- **LIM-003**: Model complexity limited by 2GB RAM
- **LIM-004**: No remote monitoring or diagnostics capability
- **LIM-005**: Camera range limited by lens and mounting position
- **LIM-006**: Night detection dependent on IR illumination or moonlight

### 12.2 Operational Limitations
- **LIM-007**: Effectiveness depends on animal response to audio deterrents
- **LIM-008**: Animals may habituate to deterrents over time
- **LIM-009**: Weather conditions may affect camera visibility
- **LIM-010**: Battery life limits continuous high-power audio use
- **LIM-011**: No real-time alerts to farmers (offline system)

### 12.3 Risks

#### 12.3.1 Technical Risks
- **RISK-001**: Model overfitting due to limited training data
- **RISK-002**: False positives causing unnecessary audio activation
- **RISK-003**: False negatives allowing animal intrusion
- **RISK-004**: Hardware failure in remote deployment
- **RISK-005**: Storage corruption from power loss

#### 12.3.2 Environmental Risks
- **RISK-006**: Extreme weather damaging equipment
- **RISK-007**: Dust and debris affecting camera performance
- **RISK-008**: Battery degradation in high temperatures
- **RISK-009**: Lightning damage to electronics

#### 12.3.3 Operational Risks
- **RISK-010**: User error during configuration
- **RISK-011**: Insufficient training data quality
- **RISK-012**: Audio deterrent ineffectiveness
- **RISK-013**: Delayed maintenance causing system failure

---

## 13. Future Scope

### 13.1 Potential Enhancements
- **FUT-001**: Upgrade to Jetson Nano 4GB or Jetson Xavier NX for improved performance
- **FUT-002**: Add thermal cameras for improved night detection
- **FUT-003**: Implement multi-stage deterrence (audio escalation)
- **FUT-004**: Add physical deterrents (lights, water spray)
- **FUT-005**: Support for additional animal species
- **FUT-006**: Optional LoRa connectivity for remote status monitoring
- **FUT-007**: Solar panel integration for extended battery life
- **FUT-008**: Advanced analytics (animal behavior patterns)
- **FUT-009**: Federated learning across multiple FINDEM units
- **FUT-010**: Integration with farm management systems

### 13.2 Research Opportunities
- **FUT-011**: Adaptive deterrence based on animal response
- **FUT-012**: Acoustic analysis for animal identification
- **FUT-013**: Predictive modeling for animal intrusion patterns
- **FUT-014**: Energy-efficient inference optimization
- **FUT-015**: Transfer learning from pre-trained wildlife models

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Product Manager | | | |
| Systems Engineer | | | |
| Technical Lead | | | |
| Stakeholder Representative | | | |

---

**End of Document**
