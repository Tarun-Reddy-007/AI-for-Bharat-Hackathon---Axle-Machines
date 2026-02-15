# FINDEM – Fauna Invasion Detection & Elimination Mechanism
## System Design Document

**Version:** 1.0  
**Date:** February 15, 2026  
**Status:** Draft  
**Related Documents:** requirements.md

---

## 1. Introduction

### 1.1 Purpose
This document describes the system design for FINDEM, detailing the architecture, components, data flows, and implementation strategies for building an offline edge-AI animal deterrence system.

### 1.2 Design Goals
- Maximize detection accuracy within Jetson Nano 2GB constraints
- Minimize detection-to-deterrent latency (<2 seconds)
- Ensure robust 24/7 operation in harsh agricultural environments
- Provide simple, intuitive physical interface for non-technical users
- Enable fully offline training and inference
- Optimize power consumption for extended battery operation

### 1.3 Design Principles
- **Edge-first**: All processing occurs on-device with no cloud dependency
- **Fail-safe**: System degrades gracefully under component failures
- **Resource-aware**: Design optimized for 2GB RAM and limited compute
- **Deterministic**: Predictable behavior for safety-critical deterrence
- **Maintainable**: Modular architecture for field serviceability

---

## 2. High-Level Architecture

### 2.1 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FINDEM SYSTEM                            │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Camera 1   │  │   Camera 2   │  │   Camera 3   │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                   │
│         └──────────────────┴──────────────────┘                  │
│                            │                                      │
│                  ┌─────────▼─────────┐                          │
│                  │  Camera Manager   │                          │
│                  └─────────┬─────────┘                          │
│                            │                                      │
│         ┌──────────────────┴──────────────────┐                 │
│         │                                       │                 │
│  ┌──────▼────────┐                   ┌────────▼────────┐       │
│  │   Training    │                   │    Detection     │       │
│  │   Pipeline    │                   │    Pipeline      │       │
│  └──────┬────────┘                   └────────┬────────┘       │
│         │                                       │                 │
│         │         ┌──────────────┐             │                 │
│         └────────►│  Model Store │◄────────────┘                │
│                   └──────────────┘                               │
│                                                                   │
│                   ┌──────────────┐                               │
│                   │ State Machine│                               │
│                   │  Controller  │                               │
│                   └───┬──────┬───┘                              │
│                       │      │                                    │
│         ┌─────────────┘      └─────────────┐                    │
│         │                                    │                    │
│  ┌──────▼────────┐                 ┌───────▼────────┐          │
│  │  UI Manager   │                 │ Audio Engine   │          │
│  │ (Keypad/LED)  │                 │  (Deterrence)  │          │
│  └───────────────┘                 └────────┬───────┘          │
│                                               │                   │
│                                      ┌────────▼────────┐         │
│                                      │  Speaker 1 & 2  │         │
│                                      └─────────────────┘         │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Power Management & Watchdog System             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Architectural Layers


**Layer 1: Hardware Abstraction Layer (HAL)**
- Camera interface drivers (CSI/USB)
- GPIO control for keypad and LEDs
- Audio output interface (ALSA)
- Power monitoring interface

**Layer 2: Core Services**
- Camera Manager: Multi-camera capture and frame buffering
- Model Store: Model persistence and versioning
- Configuration Manager: Settings persistence and validation
- Logging Service: Event logging with rotation

**Layer 3: Application Logic**
- Training Pipeline: Data augmentation, blending, model training
- Detection Pipeline: Real-time inference and detection logic
- Audio Engine: Deterrent selection and playback control
- State Machine Controller: Mode management and transitions

**Layer 4: User Interface**
- UI Manager: Keypad input processing and LED control
- Command Interpreter: Keypad command parsing and execution

**Layer 5: System Services**
- Power Manager: Battery monitoring and power optimization
- Watchdog: Health monitoring and auto-recovery
- Error Handler: Fault detection and graceful degradation

---

## 3. Hardware Architecture

### 3.1 Physical Component Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    Weatherproof Enclosure                    │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Jetson Nano 2GB Module                   │  │
│  │  ┌────────┐  ┌────────┐  ┌──────────┐               │  │
│  │  │ CPU    │  │ GPU    │  │ 2GB RAM  │               │  │
│  │  │ 4-core │  │ 128-   │  │ LPDDR4   │               │  │
│  │  │ ARM    │  │ core   │  │          │               │  │
│  │  └────────┘  └────────┘  └──────────┘               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  64GB+ SD    │  │  GPIO Exp.   │  │  USB Hub     │     │
│  │  Card/eMMC   │  │  Board       │  │  (4-port)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Power Distribution Board                             │  │
│  │  - 12V to 5V Buck Converter (Jetson, Cameras)        │  │
│  │  - 12V Audio Amplifier Power                         │  │
│  │  - Overcurrent Protection                            │  │
│  │  - Low-Voltage Cutoff                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User Interface Panel (External Mount)                │  │
│  │  ┌────────────┐  ┌──────┐  ┌──────────────────┐     │  │
│  │  │  Numeric   │  │START │  │  ●  ●  ●         │     │  │
│  │  │  Keypad    │  │Button│  │  R  Y  G  (LEDs) │     │  │
│  │  │  (0-9,*,#) │  │      │  │                   │     │  │
│  │  └────────────┘  └──────┘  └──────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

External Connections:
- Camera 1, 2, 3: Weatherproof cable glands
- Speaker 1, 2: Weatherproof cable glands
- Battery: Anderson connector or terminal block
- Solar Panel (optional): MC4 connector
```


### 3.2 Camera Subsystem Design

**Camera Configuration:**
- Primary interface: CSI (Camera Serial Interface) for low latency
- Fallback: USB cameras if CSI ports exhausted
- Resolution: 1920x1080 @ 30fps per camera
- Format: YUV422 or RGB888
- IR capability: 850nm IR LEDs for night vision

**Camera Placement Strategy:**
- Camera 1: Primary perimeter coverage (wide angle)
- Camera 2: Secondary zone or alternate angle
- Camera 3: Backup or high-risk entry point

**Frame Synchronization:**
- Cameras operate independently (no hardware sync)
- Software timestamps for frame correlation
- Round-robin processing to balance load

### 3.3 Audio Subsystem Design

**Audio Hardware:**
- USB audio adapter (C-Media or equivalent)
- Class-D amplifier: 2x100W stereo output
- PA horn speakers: 100W RMS, 8Ω impedance
- Frequency response: 300Hz - 8kHz (optimized for animal hearing)

**Audio Signal Path:**
```
Jetson Nano → USB Audio → Amplifier → Speaker 1
                                    → Speaker 2
```

**Protection Circuitry:**
- Thermal shutdown on amplifier
- Current limiting per channel
- Soft-start to prevent speaker damage

### 3.4 Power Subsystem Design

**Power Budget:**
```
Component              Power (W)    Duty Cycle    Avg Power (W)
─────────────────────────────────────────────────────────────
Jetson Nano            10           100%          10
Camera 1               5            100%          5
Camera 2               5            100%          5
Camera 3               5            100%          5
Keypad/LEDs            2            100%          2
Audio (standby)        3            100%          3
Audio (active)         200          5%            10
─────────────────────────────────────────────────────────────
Total Continuous:      30W
Total with Audio:      40W average
```

**Battery Sizing:**
- Capacity: 12V 100Ah (1200Wh)
- Runtime (no audio): 40 hours
- Runtime (with audio): 30 hours
- Target: 24-hour minimum operation

**Solar Charging (Optional):**
- Panel: 100W, 12V nominal
- Controller: MPPT, 10A
- Daily energy: ~400Wh (4 hours equivalent sunlight)
- Net consumption: 720Wh/day (30W × 24h)
- Solar contribution: 55% of daily needs

---

## 4. Software Architecture

### 4.1 Software Stack

```
┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Training   │  │  Detection   │  │  UI Manager  │ │
│  │   Pipeline   │  │  Pipeline    │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Camera     │  │    Audio     │  │    Power     │ │
│  │   Manager    │  │    Engine    │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Framework Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  PyTorch +   │  │   OpenCV     │  │    ALSA      │ │
│  │  TensorRT    │  │   GStreamer  │  │  PyAudio     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│                  Operating System                        │
│         Ubuntu 18.04 + JetPack SDK 4.6.x                │
│              Linux Kernel 4.9 (ARM64)                    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Core Modules

**Module: Camera Manager**
- Responsibilities:
  - Initialize and configure camera devices
  - Capture frames from multiple cameras
  - Maintain frame buffers (ring buffer, 30 frames)
  - Handle camera disconnection/reconnection
  - Provide frame access to pipelines

**Module: Training Pipeline**
- Responsibilities:
  - Coordinate training workflow
  - Invoke data augmentation
  - Invoke image blending
  - Execute YOLO training
  - Save model checkpoints
  - Report training progress

**Module: Detection Pipeline**
- Responsibilities:
  - Load trained model (TensorRT optimized)
  - Process frames from Camera Manager
  - Run inference on each frame
  - Apply confidence thresholding
  - Trigger audio deterrence on detection
  - Log detection events

**Module: Audio Engine**
- Responsibilities:
  - Maintain audio file library
  - Implement randomization algorithm
  - Manage playback queue
  - Control volume and duration
  - Enforce cooldown periods
  - Provide test playback capability


**Module: State Machine Controller**
- Responsibilities:
  - Manage system operational modes
  - Enforce mode transition rules
  - Coordinate module activation/deactivation
  - Handle mode-specific logic
  - Persist current state

**Module: UI Manager**
- Responsibilities:
  - Poll keypad for input
  - Debounce button presses
  - Parse command sequences
  - Control LED states and patterns
  - Provide audio feedback (beeps)
  - Execute user commands

**Module: Power Manager**
- Responsibilities:
  - Monitor battery voltage and current
  - Calculate state of charge (SoC)
  - Trigger low-battery warnings
  - Initiate graceful shutdown
  - Log power events
  - Optimize power consumption

**Module: Watchdog Service**
- Responsibilities:
  - Monitor application health
  - Detect deadlocks and hangs
  - Restart application on failure
  - Log crash events
  - Implement exponential backoff

### 4.3 Technology Selection

**Programming Language:**
- Primary: Python 3.6+ (rapid development, rich ecosystem)
- Performance-critical: C++ (camera capture, inference loop)
- Rationale: Python for flexibility, C++ for real-time constraints

**AI Framework:**
- Training: PyTorch 1.10+ (ease of use, dynamic graphs)
- Inference: TensorRT 8.x (optimized for Jetson)
- Model: YOLOv5 or YOLOv7 (balance of speed and accuracy)
- Rationale: PyTorch for training flexibility, TensorRT for inference speed

**Computer Vision:**
- Library: OpenCV 4.5+ with CUDA support
- Camera: GStreamer pipelines for hardware acceleration
- Augmentation: Albumentations (fast, comprehensive)
- Rationale: Hardware-accelerated processing on Jetson GPU

**Audio:**
- Playback: PyAudio + ALSA
- Format: WAV (uncompressed, low latency)
- Rationale: Simple, deterministic playback

**Data Storage:**
- Configuration: JSON files
- Logs: SQLite database
- Images: Filesystem (organized by class)
- Model: PyTorch .pt and TensorRT .engine files
- Rationale: Simple, no external dependencies

---

## 5. Component Diagram Description

### 5.1 Component Interaction

```
┌─────────────┐
│   Keypad    │──┐
└─────────────┘  │
                 │    ┌──────────────────┐
┌─────────────┐  ├───►│   UI Manager     │
│ Start Button│──┘    └────────┬─────────┘
└─────────────┘                │
                               │ Commands
                               ▼
                    ┌──────────────────────┐
                    │  State Machine       │
                    │  Controller          │
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │               │
                ▼              ▼               ▼
    ┌───────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Training    │  │  Detection   │  │    Config    │
    │   Pipeline    │  │  Pipeline    │  │    Mode      │
    └───────┬───────┘  └──────┬───────┘  └──────────────┘
            │                  │
            │                  │
            ▼                  ▼
    ┌───────────────┐  ┌──────────────┐
    │    Camera     │  │    Model     │
    │    Manager    │  │    Store     │
    └───────────────┘  └──────────────┘
                               │
                               │ Detection Event
                               ▼
                       ┌──────────────┐
                       │    Audio     │
                       │    Engine    │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Speakers   │
                       └──────────────┘
```

### 5.2 Inter-Component Communication

**Communication Mechanism:**
- Event-driven architecture using Python queues
- Producer-consumer pattern for frame processing
- Callback pattern for asynchronous events
- Shared memory for configuration access

**Key Interfaces:**

```python
# Camera Manager Interface
class ICameraManager:
    def get_frame(camera_id: int) -> np.ndarray
    def get_all_frames() -> List[np.ndarray]
    def is_camera_active(camera_id: int) -> bool

# Detection Pipeline Interface
class IDetectionPipeline:
    def process_frame(frame: np.ndarray, camera_id: int) -> List[Detection]
    def set_confidence_threshold(threshold: float) -> None

# Audio Engine Interface
class IAudioEngine:
    def play_deterrent(animal_class: str) -> None
    def test_audio() -> None
    def set_volume(level: int) -> None

# State Machine Interface
class IStateMachine:
    def transition_to(state: SystemState) -> bool
    def get_current_state() -> SystemState
    def can_transition(target_state: SystemState) -> bool
```

---

## 6. Data Flow Design

### 6.1 Training Mode Data Flow

```
User Input (Keypad)
    │
    ├─► "1" = Elephant
    ├─► "2" = Wild Boar
    ├─► "3" = Monkey
    └─► "4" = Deer
    │
    ▼
[Capture Image] ──► Camera Manager ──► Raw Image
    │                                      │
    │                                      ▼
    │                              [Save to Disk]
    │                              /data/raw/{class}/img_{timestamp}.jpg
    │
    ▼
[Press START Button]
    │
    ▼
Training Pipeline Activated
    │
    ├─► Load Raw Images
    │       │
    │       ▼
    ├─► Data Augmentation Module
    │       │ (Rotation, Scale, Brightness, Flip, Noise)
    │       │
    │       ▼
    │   Augmented Images (5x per source)
    │   /data/augmented/{class}/
    │       │
    │       ▼
    ├─► Image Blending Module
    │       │ (Blend animals onto backgrounds)
    │       │
    │       ▼
    │   Composite Images
    │   /data/composite/{class}/
    │       │
    │       ▼
    ├─► Generate YOLO Annotations
    │       │ (Bounding boxes, class labels)
    │       │
    │       ▼
    │   dataset.yaml, labels/*.txt
    │       │
    │       ▼
    └─► YOLO Training
            │ (YOLOv5/v7 train.py)
            │
            ├─► Epoch Progress ──► LED Blink Pattern
            │
            ▼
        Trained Model
        /models/findem_model.pt
            │
            ▼
        TensorRT Conversion
        /models/findem_model.engine
            │
            ▼
        [Training Complete] ──► LED: Solid Green
```


### 6.2 Detection Mode Data Flow

```
System Startup
    │
    ▼
Load TensorRT Model (/models/findem_model.engine)
    │
    ▼
Initialize Camera Manager (Cameras 1, 2, 3)
    │
    ▼
[Detection Loop - Continuous]
    │
    ├─► Camera 1 ──► Frame Buffer 1 ──┐
    ├─► Camera 2 ──► Frame Buffer 2 ──┤
    └─► Camera 3 ──► Frame Buffer 3 ──┤
                                       │
                                       ▼
                            [Frame Preprocessor]
                            - Resize to 640x640
                            - Normalize [0, 1]
                            - Convert to tensor
                                       │
                                       ▼
                            [TensorRT Inference]
                            - Forward pass
                            - NMS (Non-Max Suppression)
                                       │
                                       ▼
                            [Detection Results]
                            [{class, confidence, bbox}, ...]
                                       │
                                       ▼
                            [Confidence Filter]
                            (threshold = 0.6 default)
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                      │
                    ▼                                      ▼
            [No Detection]                        [Animal Detected!]
            - Continue loop                       - Log event
            - LED: Solid Green                    - LED: Rapid blink
                                                  - Trigger Audio Engine
                                                          │
                                                          ▼
                                                  [Audio Engine]
                                                  - Select random audio
                                                  - Play deterrent
                                                  - Start cooldown timer
                                                          │
                                                          ▼
                                                  [Speakers Activate]
                                                  - Duration: 10-30 sec
                                                  - Volume: Configured
                                                          │
                                                          ▼
                                                  [Cooldown Period]
                                                  - 60 seconds
                                                  - Prevent audio spam
                                                          │
                                                          ▼
                                                  [Resume Detection]
```

### 6.3 Configuration Mode Data Flow

```
User Keypad Input: "*" + Command + "#"
    │
    ▼
[Command Parser]
    │
    ├─► *11# = Set confidence threshold (next 2 digits)
    ├─► *22# = Set audio volume (next 2 digits, 0-99)
    ├─► *33# = Test audio
    ├─► *44# = View battery status (LED blink count)
    ├─► *99# = Factory reset
    │
    ▼
[Configuration Manager]
    │
    ├─► Validate input
    ├─► Update config.json
    ├─► Apply changes
    └─► LED feedback (Green = success, Red = error)
```

---

## 7. Training Pipeline Design

### 7.1 Training Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Training Pipeline                         │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 1: Data Collection                              │ │
│  │  - Capture images via Camera Manager                   │ │
│  │  - User labels via keypad (1=Elephant, 2=Boar, etc.)  │ │
│  │  - Store: /data/raw/{class}/                           │ │
│  │  - Target: 50-200 images per class                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 2: Data Augmentation                            │ │
│  │  - Load raw images                                     │ │
│  │  - Apply transformations:                              │ │
│  │    • Rotation: ±15 degrees                             │ │
│  │    • Scale: 0.8x to 1.2x                               │ │
│  │    • Brightness: ±20%                                  │ │
│  │    • Horizontal flip: 50% probability                  │ │
│  │    • Gaussian noise: σ=5                               │ │
│  │  - Generate 5 variants per source image                │ │
│  │  - Store: /data/augmented/{class}/                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 3: Image Blending                               │ │
│  │  - Load augmented animal images                        │ │
│  │  - Load background images (farm scenes)                │ │
│  │  - Blending algorithm:                                 │ │
│  │    1. Extract animal foreground (segmentation)         │ │
│  │    2. Random position on background                    │ │
│  │    3. Random scale (0.1x to 0.5x of background)        │ │
│  │    4. Alpha blending with edge smoothing               │ │
│  │    5. Color matching (histogram matching)              │ │
│  │  - Generate bounding box annotations                   │ │
│  │  - Store: /data/composite/{class}/                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 4: Dataset Preparation                          │ │
│  │  - Combine all composite images                        │ │
│  │  - Generate YOLO format annotations:                   │ │
│  │    <class_id> <x_center> <y_center> <width> <height>  │ │
│  │  - Split: 80% train, 20% validation                    │ │
│  │  - Create dataset.yaml configuration                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 5: Model Training                               │ │
│  │  - Model: YOLOv5s or YOLOv7-tiny                       │ │
│  │  - Input size: 640x640                                 │ │
│  │  - Batch size: 8 (memory constraint)                   │ │
│  │  - Epochs: 100-300                                     │ │
│  │  - Optimizer: SGD with momentum                        │ │
│  │  - Learning rate: 0.01 with cosine decay               │ │
│  │  - Augmentation: Mosaic, mixup (built-in YOLO)        │ │
│  │  - Early stopping: Patience = 50 epochs                │ │
│  │  - Checkpoint: Save best model by mAP                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Stage 6: Model Optimization                           │ │
│  │  - Convert PyTorch model to ONNX                       │ │
│  │  - Convert ONNX to TensorRT engine                     │ │
│  │  - Precision: FP16 (2x speedup on Jetson)              │ │
│  │  - Optimize for batch size = 1                         │ │
│  │  - Validate accuracy (mAP drop < 2%)                   │ │
│  │  - Store: /models/findem_model.engine                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Data Augmentation Implementation

**Augmentation Pipeline (using Albumentations):**

```python
import albumentations as A

augmentation_pipeline = A.Compose([
    A.Rotate(limit=15, p=0.8),
    A.RandomScale(scale_limit=0.2, p=0.8),
    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.8),
    A.HorizontalFlip(p=0.5),
    A.GaussNoise(var_limit=(5.0, 20.0), p=0.5),
    A.RandomGamma(gamma_limit=(80, 120), p=0.5),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
```


### 7.3 Image Blending Algorithm

**Blending Strategy:**

```
Input: Animal image (foreground), Farm background image
Output: Composite image with bounding box annotation

Algorithm:
1. Foreground Extraction:
   - Use GrabCut or simple thresholding
   - Generate alpha mask for animal
   - Refine edges with morphological operations

2. Placement:
   - Random position: (x, y) within background bounds
   - Constraint: Full animal must fit in frame
   - Avoid edges (10% margin)

3. Scaling:
   - Target size: 10-50% of background dimension
   - Maintain aspect ratio
   - Realistic size for animal type

4. Blending:
   - Alpha compositing: result = fg * alpha + bg * (1 - alpha)
   - Feather edges: Gaussian blur on alpha mask (σ=2)
   - Color matching: Match histogram of fg to bg region

5. Annotation:
   - Calculate bounding box from alpha mask
   - Convert to YOLO format (normalized coordinates)
   - Save as {image_name}.txt

6. Quality Check:
   - Verify bbox within [0, 1] range
   - Ensure minimum size (>32x32 pixels)
   - Discard if blending artifacts detected
```

### 7.4 Training Hyperparameters

**Model Configuration:**
```yaml
model: yolov5s  # Small model for Jetson Nano
input_size: 640
classes: 4  # Elephant, Boar, Monkey, Deer
depth_multiple: 0.33
width_multiple: 0.50
```

**Training Configuration:**
```yaml
epochs: 200
batch_size: 8
learning_rate: 0.01
momentum: 0.937
weight_decay: 0.0005
warmup_epochs: 3
warmup_momentum: 0.8
warmup_bias_lr: 0.1
optimizer: SGD
lr_scheduler: cosine
```

**Memory Management:**
- Clear cache after each epoch
- Use gradient accumulation if OOM
- Limit dataloader workers to 2
- Enable mixed precision training (FP16)

---

## 8. Detection Pipeline Design

### 8.1 Detection Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Detection Pipeline                         │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Initialization Phase                                   │ │
│  │  1. Load TensorRT engine                               │ │
│  │  2. Allocate GPU memory buffers                        │ │
│  │  3. Initialize camera streams                          │ │
│  │  4. Load configuration (thresholds, etc.)              │ │
│  │  5. Initialize audio engine                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frame Acquisition (Multi-threaded)                    │ │
│  │                                                         │ │
│  │  Thread 1: Camera 1 → Buffer 1 (30 frames ring)       │ │
│  │  Thread 2: Camera 2 → Buffer 2 (30 frames ring)       │ │
│  │  Thread 3: Camera 3 → Buffer 3 (30 frames ring)       │ │
│  │                                                         │ │
│  │  Frame rate: 30 FPS per camera                         │ │
│  │  Format: RGB888, 1920x1080                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Frame Preprocessing (GPU-accelerated)                 │ │
│  │  1. Resize: 1920x1080 → 640x640 (letterbox)           │ │
│  │  2. Normalize: [0, 255] → [0, 1]                       │ │
│  │  3. Transpose: HWC → CHW                               │ │
│  │  4. Convert to CUDA tensor                             │ │
│  │  Time budget: <20ms                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  TensorRT Inference                                    │ │
│  │  - Input: [1, 3, 640, 640] tensor                      │ │
│  │  - Forward pass through optimized engine               │ │
│  │  - Output: [1, 25200, 9] tensor                        │ │
│  │    (25200 anchors, 9 = 4 bbox + 1 conf + 4 classes)   │ │
│  │  - Inference time: ~50-100ms (10-20 FPS)               │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Post-processing                                       │ │
│  │  1. Apply confidence threshold (default: 0.6)          │ │
│  │  2. Non-Maximum Suppression (NMS)                      │ │
│  │     - IoU threshold: 0.45                              │ │
│  │     - Max detections: 100                              │ │
│  │  3. Scale bboxes back to original resolution           │ │
│  │  4. Filter by class (only target animals)              │ │
│  │  Time budget: <10ms                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Detection Decision Logic                              │ │
│  │                                                         │ │
│  │  IF detections.count > 0:                              │ │
│  │    - Get highest confidence detection                  │ │
│  │    - Extract animal class                              │ │
│  │    - Log event (timestamp, class, confidence, camera)  │ │
│  │    - Trigger audio deterrence                          │ │
│  │  ELSE:                                                 │ │
│  │    - Continue to next frame                            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Multi-Camera Processing Strategy

**Round-Robin Processing:**
```
Time    Camera    Action
────────────────────────────────────
0ms     Cam1      Capture + Inference
100ms   Cam2      Capture + Inference
200ms   Cam3      Capture + Inference
300ms   Cam1      Capture + Inference
...
```

**Effective frame rate per camera: ~3-5 FPS**

**Alternative: Parallel Processing (if performance allows):**
```
Thread 1: Cam1 → Inference Engine 1
Thread 2: Cam2 → Inference Engine 2 (shared)
Thread 3: Cam3 → Inference Engine 3 (shared)
```

**Memory constraint: Single TensorRT engine shared across threads**

### 8.3 Detection Confidence Tuning

**Confidence Threshold Strategy:**
- Default: 0.6 (balance precision/recall)
- Conservative: 0.75 (minimize false positives)
- Aggressive: 0.4 (maximize recall, more false positives)

**Per-Class Thresholds (optional):**
```python
thresholds = {
    'elephant': 0.5,  # Lower threshold (critical threat)
    'boar': 0.6,      # Standard
    'monkey': 0.65,   # Higher (more false positives)
    'deer': 0.6       # Standard
}
```

### 8.4 Performance Optimization

**Optimization Techniques:**
1. TensorRT FP16 precision (2x speedup)
2. CUDA streams for async processing
3. Zero-copy memory between CPU/GPU
4. Batch size = 1 (minimize latency)
5. GStreamer hardware video decode
6. Preallocate all buffers at startup

**Target Performance:**
- Inference: 50-100ms per frame
- End-to-end latency: <200ms (capture to detection)
- Detection-to-audio: <2 seconds (requirement)

---

## 9. Anti-Habituation Audio Engine Design

### 9.1 Audio Engine Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Audio Engine                              │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Audio Library Structure                                │ │
│  │                                                         │ │
│  │  /audio/                                                │ │
│  │    ├── elephant/                                        │ │
│  │    │   ├── elephant_01.wav                              │ │
│  │    │   ├── elephant_02.wav                              │ │
│  │    │   └── ... (10-20 variants)                         │ │
│  │    ├── boar/                                            │ │
│  │    │   └── ... (10-20 variants)                         │ │
│  │    ├── monkey/                                          │ │
│  │    │   └── ... (10-20 variants)                         │ │
│  │    ├── deer/                                            │ │
│  │    │   └── ... (10-20 variants)                         │ │
│  │    └── generic/                                         │ │
│  │        └── ... (fallback sounds)                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Randomization Algorithm                                │ │
│  │                                                         │ │
│  │  1. Receive detection event (animal_class)             │ │
│  │  2. Load audio file list for class                     │ │
│  │  3. Exclude recently played files (history = 5)        │ │
│  │  4. Select random file from remaining                  │ │
│  │  5. Add to play history                                │ │
│  │  6. Queue for playback                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Playback Controller                                   │ │
│  │  - Check cooldown timer (60 seconds default)           │ │
│  │  - If cooldown active: Queue for later                 │ │
│  │  - If ready: Start playback                            │ │
│  │  - Apply volume scaling                                │ │
│  │  - Monitor playback duration                           │ │
│  │  - Auto-stop after max duration (30 seconds)           │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Audio Output (ALSA)                                   │ │
│  │  - Device: USB audio adapter                           │ │
│  │  - Format: 16-bit PCM, 44.1kHz, Stereo                 │ │
│  │  - Buffer size: 1024 samples                           │ │
│  │  - Latency: ~23ms                                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```


### 9.2 Anti-Habituation Strategy

**Problem:** Animals may become habituated to repeated identical sounds, reducing deterrent effectiveness.

**Solution: Multi-Layer Randomization**

**Layer 1: Audio Variant Selection**
- Maintain 10-20 different audio files per animal class
- Each file contains different sound characteristics:
  - Different source recordings
  - Different pitch variations
  - Different temporal patterns
  - Different intensity profiles

**Layer 2: Playback Randomization**
- Random selection from available variants
- Exclude recently played files (history window = 5)
- Weighted random selection (prefer less-used files)

**Layer 3: Temporal Randomization**
- Variable playback duration (10-30 seconds)
- Random start position within audio file
- Variable cooldown period (60-120 seconds)

**Layer 4: Spatial Randomization (if 2 speakers)**
- Alternate between speakers
- Random speaker selection
- Stereo panning effects

**Implementation:**
```python
class AntiHabituationEngine:
    def __init__(self):
        self.play_history = deque(maxlen=5)
        self.usage_count = defaultdict(int)
    
    def select_audio(self, animal_class):
        # Get all audio files for class
        available = self.get_audio_files(animal_class)
        
        # Exclude recently played
        candidates = [f for f in available if f not in self.play_history]
        
        # Weighted selection (prefer less-used)
        weights = [1.0 / (self.usage_count[f] + 1) for f in candidates]
        selected = random.choices(candidates, weights=weights)[0]
        
        # Update history
        self.play_history.append(selected)
        self.usage_count[selected] += 1
        
        return selected
```

### 9.3 Audio Content Design

**Audio Types:**

1. **Predator Sounds:**
   - Tiger roars
   - Lion growls
   - Dog barking
   - Human shouting

2. **Distress Calls:**
   - Conspecific alarm calls
   - Prey distress sounds

3. **Startling Sounds:**
   - Gunshots
   - Firecrackers
   - Air horns
   - Metallic clanging

4. **Ultrasonic Components (if hardware supports):**
   - High-frequency tones (18-22 kHz)
   - Frequency sweeps

**Audio Specifications:**
- Format: WAV (uncompressed)
- Sample rate: 44.1 kHz
- Bit depth: 16-bit
- Channels: Stereo
- Duration: 10-30 seconds per file
- Peak amplitude: -3 dBFS (prevent clipping)

### 9.4 Cooldown and Rate Limiting

**Cooldown Logic:**
```python
class CooldownManager:
    def __init__(self, cooldown_seconds=60):
        self.cooldown_seconds = cooldown_seconds
        self.last_activation = 0
    
    def can_activate(self):
        now = time.time()
        if now - self.last_activation >= self.cooldown_seconds:
            return True
        return False
    
    def activate(self):
        self.last_activation = time.time()
    
    def time_remaining(self):
        elapsed = time.time() - self.last_activation
        return max(0, self.cooldown_seconds - elapsed)
```

**Rate Limiting Rules:**
- Minimum cooldown: 60 seconds
- Maximum activations per hour: 30
- Maximum activations per day: 200
- Adaptive cooldown: Increase if detections are frequent

---

## 10. State Machine Design

### 10.1 System States

```
┌─────────────────────────────────────────────────────────────┐
│                    System State Machine                      │
│                                                               │
│                      ┌──────────┐                            │
│                      │   BOOT   │                            │
│                      └────┬─────┘                            │
│                           │                                   │
│                           ▼                                   │
│                      ┌──────────┐                            │
│                      │   INIT   │                            │
│                      └────┬─────┘                            │
│                           │                                   │
│              ┌────────────┴────────────┐                     │
│              │                          │                     │
│              ▼                          ▼                     │
│       ┌─────────────┐           ┌─────────────┐             │
│   ┌──│   TRAINING  │           │  DETECTION  │──┐           │
│   │  └─────────────┘           └─────────────┘  │           │
│   │         │                          │         │           │
│   │         │                          │         │           │
│   │         └──────────┬───────────────┘         │           │
│   │                    │                         │           │
│   │                    ▼                         │           │
│   │             ┌─────────────┐                 │           │
│   └────────────►│    CONFIG   │◄────────────────┘           │
│                 └──────┬──────┘                              │
│                        │                                      │
│                        ▼                                      │
│                 ┌─────────────┐                              │
│                 │ DIAGNOSTIC  │                              │
│                 └──────┬──────┘                              │
│                        │                                      │
│                        ▼                                      │
│                 ┌─────────────┐                              │
│                 │    ERROR    │                              │
│                 └──────┬──────┘                              │
│                        │                                      │
│                        ▼                                      │
│                 ┌─────────────┐                              │
│                 │  SHUTDOWN   │                              │
│                 └─────────────┘                              │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 State Descriptions

**BOOT State:**
- Entry: Power-on or reset
- Actions:
  - Initialize hardware (GPIO, cameras, audio)
  - Load configuration
  - Perform self-test
  - LED: All blink
- Exit: Transition to INIT
- Duration: <10 seconds

**INIT State:**
- Entry: From BOOT
- Actions:
  - Load trained model (if exists)
  - Initialize camera streams
  - Initialize audio engine
  - Determine default mode (DETECTION if model exists, else CONFIG)
  - LED: Yellow solid
- Exit: Transition to DETECTION or CONFIG
- Duration: <30 seconds

**TRAINING State:**
- Entry: User presses START button
- Actions:
  - Stop detection pipeline
  - Load training data
  - Execute training pipeline
  - Update LED progress (blink rate = epoch progress)
  - Save trained model
  - LED: Yellow blinking (rate increases with progress)
- Exit: Transition to DETECTION on completion
- Duration: 12-24 hours
- Interrupts: User can abort with keypad command

**DETECTION State:**
- Entry: From INIT or TRAINING completion
- Actions:
  - Load TensorRT model
  - Start camera capture
  - Run detection loop
  - Trigger audio on detection
  - LED: Green solid (normal), Green rapid blink (detection)
- Exit: User command to CONFIG or TRAINING
- Duration: Indefinite (24/7 operation)

**CONFIG State:**
- Entry: User keypad command (*00#)
- Actions:
  - Pause detection
  - Accept configuration commands
  - Update settings
  - Provide LED feedback
  - LED: Yellow solid
- Exit: User command to return to DETECTION
- Duration: User-controlled

**DIAGNOSTIC State:**
- Entry: User keypad command (*99#)
- Actions:
  - Run hardware tests
  - Test cameras (capture test images)
  - Test audio (play test sound)
  - Test LEDs (cycle patterns)
  - Report battery status (LED blink count)
  - LED: All LEDs cycle
- Exit: Automatic return to previous state
- Duration: <60 seconds

**ERROR State:**
- Entry: Critical error detected
- Actions:
  - Log error details
  - Attempt recovery
  - LED: Red blinking (error code)
- Exit: Recovery to INIT or SHUTDOWN
- Duration: Variable

**SHUTDOWN State:**
- Entry: Low battery or user command
- Actions:
  - Save state
  - Close camera streams
  - Flush logs
  - Power down peripherals
  - LED: All off
- Exit: Power off
- Duration: <10 seconds


### 10.3 State Transition Rules

**Transition Table:**

| From State  | To State   | Trigger                          | Conditions                    |
|-------------|------------|----------------------------------|-------------------------------|
| BOOT        | INIT       | Automatic                        | Self-test passed              |
| BOOT        | ERROR      | Automatic                        | Self-test failed              |
| INIT        | DETECTION  | Automatic                        | Model exists                  |
| INIT        | CONFIG     | Automatic                        | No model exists               |
| DETECTION   | TRAINING   | START button                     | Not in cooldown               |
| DETECTION   | CONFIG     | Keypad: *00#                     | Always allowed                |
| DETECTION   | DIAGNOSTIC | Keypad: *99#                     | Always allowed                |
| DETECTION   | ERROR      | Critical fault                   | Hardware failure              |
| DETECTION   | SHUTDOWN   | Low battery                      | Battery < 5%                  |
| TRAINING    | DETECTION  | Training complete                | Model saved successfully      |
| TRAINING    | ERROR      | Training failed                  | OOM or other error            |
| CONFIG      | DETECTION  | Keypad: *00#                     | Always allowed                |
| CONFIG      | TRAINING   | START button                     | Always allowed                |
| DIAGNOSTIC  | Previous   | Test complete                    | Automatic                     |
| ERROR       | INIT       | Recovery successful              | Automatic                     |
| ERROR       | SHUTDOWN   | Recovery failed                  | After 3 attempts              |
| Any         | SHUTDOWN   | Keypad: *999#                    | Hold for 5 seconds            |

### 10.4 State Persistence

**State Storage:**
```json
{
  "current_state": "DETECTION",
  "previous_state": "TRAINING",
  "state_entry_time": 1708012800,
  "training_progress": {
    "epoch": 150,
    "total_epochs": 200,
    "best_map": 0.87
  },
  "detection_stats": {
    "total_detections": 42,
    "last_detection_time": 1708012750,
    "detections_by_class": {
      "elephant": 5,
      "boar": 20,
      "monkey": 15,
      "deer": 2
    }
  }
}
```

**Persistence Strategy:**
- Save state to disk every 60 seconds
- Save immediately on state transition
- Load on INIT to resume operation
- Atomic write (write to temp, then rename)

---

## 11. User Interaction Flow

### 11.1 Keypad Command Structure

**Command Format:** `*<command_code>#`

**Command Codes:**

| Code  | Function                          | Parameters        | Example      |
|-------|-----------------------------------|-------------------|--------------|
| *00#  | Enter/Exit CONFIG mode            | None              | *00#         |
| *11#  | Set confidence threshold          | 2 digits (40-99)  | *11#65       |
| *22#  | Set audio volume                  | 2 digits (00-99)  | *22#75       |
| *33#  | Test audio                        | None              | *33#         |
| *44#  | Battery status                    | None              | *44#         |
| *55#  | View detection count              | None              | *55#         |
| *66#  | Clear detection log               | None              | *66#         |
| *77#  | Set cooldown period               | 2 digits (30-99s) | *77#60       |
| *88#  | Factory reset (confirm with *88#) | None              | *88#*88#     |
| *99#  | Enter DIAGNOSTIC mode             | None              | *99#         |
| *999# | Shutdown (hold 5 seconds)         | None              | *999# (hold) |
| 1-4   | Label image (TRAINING mode)       | Class ID          | 1            |

### 11.2 LED Indicator Patterns

**LED States:**

| State         | Red LED      | Yellow LED   | Green LED    | Pattern                  |
|---------------|--------------|--------------|--------------|--------------------------|
| BOOT          | Blink        | Blink        | Blink        | All blink 1Hz            |
| INIT          | Off          | Solid        | Off          | Yellow solid             |
| DETECTION     | Off          | Off          | Solid        | Green solid              |
| Detection!    | Off          | Off          | Rapid blink  | Green 5Hz for 2s         |
| TRAINING      | Off          | Slow blink   | Off          | Yellow 0.5Hz             |
| Training 50%  | Off          | Med blink    | Off          | Yellow 1Hz               |
| Training 90%  | Off          | Fast blink   | Off          | Yellow 2Hz               |
| CONFIG        | Off          | Solid        | Off          | Yellow solid             |
| DIAGNOSTIC    | Cycle        | Cycle        | Cycle        | Sequential 1s each       |
| ERROR         | Blink        | Off          | Off          | Red blink (error code)   |
| Low Battery   | Slow blink   | Off          | Solid        | Red 0.2Hz                |
| Critical Batt | Rapid blink  | Off          | Off          | Red 5Hz                  |
| SHUTDOWN      | Off          | Off          | Off          | All off                  |

**Error Code Blinks (Red LED):**
- 1 blink: Camera failure
- 2 blinks: Model load failure
- 3 blinks: Audio system failure
- 4 blinks: Storage failure
- 5 blinks: Power system failure
- Continuous: Critical system failure

### 11.3 User Workflows

**Workflow 1: Initial Setup and Training**
```
1. Power on system
   → LED: All blink (BOOT)
   → LED: Yellow solid (INIT)
   → LED: Yellow solid (CONFIG - no model)

2. Capture training images
   → Point camera at animal
   → Press "1" for Elephant (or 2, 3, 4 for other classes)
   → System captures image
   → LED: Green blink (confirmation)
   → Repeat 50-200 times per class

3. Start training
   → Press START button
   → LED: Yellow blinking (TRAINING)
   → Wait 12-24 hours
   → LED: Green solid (DETECTION - training complete)

4. System now in detection mode
   → Automatic deterrence active
```

**Workflow 2: Adjust Detection Sensitivity**
```
1. Enter CONFIG mode
   → Press *00#
   → LED: Yellow solid

2. Set confidence threshold
   → Press *11#
   → Press 2 digits (e.g., 65 for 0.65)
   → LED: Green blink (success) or Red blink (error)

3. Exit CONFIG mode
   → Press *00#
   → LED: Green solid (DETECTION)
```

**Workflow 3: Test Audio System**
```
1. Enter CONFIG mode
   → Press *00#

2. Test audio
   → Press *33#
   → Random audio plays
   → LED: Green blink during playback

3. Adjust volume if needed
   → Press *22#
   → Press 2 digits (00-99)
   → Press *33# to test again

4. Exit CONFIG mode
   → Press *00#
```

**Workflow 4: Check Battery Status**
```
1. Press *44#
   → LED blinks indicate battery level:
     - Green: 5 blinks = 100-80%
     - Green: 4 blinks = 80-60%
     - Green: 3 blinks = 60-40%
     - Yellow: 2 blinks = 40-20%
     - Red: 1 blink = 20-0%
```

**Workflow 5: Diagnostic Test**
```
1. Press *99#
   → Enter DIAGNOSTIC mode

2. System runs tests:
   → Camera test (capture from each camera)
   → Audio test (play test sound)
   → LED test (cycle all LEDs)
   → Battery test (report voltage)

3. Automatic return to previous mode
   → LED indicates test results
```

---

## 12. Error Handling and Fail-Safes

### 12.1 Error Detection Mechanisms

**Hardware Monitoring:**
```python
class HardwareMonitor:
    def check_cameras(self):
        # Verify each camera is responding
        for cam_id in [1, 2, 3]:
            if not self.camera_manager.is_active(cam_id):
                self.log_error(f"Camera {cam_id} failure")
                self.led_controller.set_error_code(1)
    
    def check_audio(self):
        # Verify audio device is present
        if not self.audio_engine.is_device_available():
            self.log_error("Audio device failure")
            self.led_controller.set_error_code(3)
    
    def check_storage(self):
        # Verify storage is writable and has space
        free_space = self.get_free_space()
        if free_space < 1_000_000_000:  # 1GB minimum
            self.log_error("Low storage space")
            self.led_controller.set_error_code(4)
    
    def check_battery(self):
        # Monitor battery voltage
        voltage = self.power_manager.get_voltage()
        if voltage < 11.0:  # Critical for 12V system
            self.log_error("Critical battery voltage")
            self.initiate_shutdown()
```

### 12.2 Graceful Degradation

**Degradation Strategies:**

**Camera Failure:**
- If 1 camera fails: Continue with remaining cameras
- If 2 cameras fail: Continue with 1 camera
- If all cameras fail: Enter ERROR state, attempt recovery

**Audio Failure:**
- Log error but continue detection
- LED indicates audio system failure
- Detection events still logged

**Storage Failure:**
- Switch to RAM-only logging (limited history)
- Disable training capability
- Continue detection operation

**Model Load Failure:**
- Attempt to reload from backup
- If backup fails, enter CONFIG mode
- Require retraining

**Power Failure (Low Battery):**
- 20% battery: LED warning, continue operation
- 10% battery: Disable audio (save power)
- 5% battery: Graceful shutdown


### 12.3 Watchdog Implementation

**Watchdog Architecture:**
```python
class WatchdogService:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self.last_heartbeat = time.time()
        self.restart_count = 0
        self.max_restarts = 3
    
    def heartbeat(self):
        """Called by main application periodically"""
        self.last_heartbeat = time.time()
    
    def check(self):
        """Called by separate watchdog thread"""
        elapsed = time.time() - self.last_heartbeat
        if elapsed > self.timeout:
            self.handle_timeout()
    
    def handle_timeout(self):
        """Application appears hung"""
        self.log_error("Watchdog timeout - application hung")
        
        if self.restart_count < self.max_restarts:
            self.restart_application()
            self.restart_count += 1
        else:
            self.log_error("Max restarts exceeded - entering safe mode")
            self.enter_safe_mode()
    
    def restart_application(self):
        """Restart main application"""
        self.save_state()
        os.system("systemctl restart findem.service")
    
    def enter_safe_mode(self):
        """Minimal operation mode"""
        # Disable training and detection
        # Only respond to keypad commands
        # LED: Red blinking
```

**Watchdog Configuration:**
- Heartbeat interval: 10 seconds
- Timeout: 30 seconds
- Max restarts: 3
- Restart backoff: Exponential (30s, 60s, 120s)

### 12.4 Data Integrity Protection

**Configuration Backup:**
```python
class ConfigManager:
    def save_config(self, config):
        # Atomic write with backup
        temp_file = "config.json.tmp"
        backup_file = "config.json.bak"
        config_file = "config.json"
        
        # Write to temp file
        with open(temp_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Backup existing config
        if os.path.exists(config_file):
            shutil.copy(config_file, backup_file)
        
        # Atomic rename
        os.rename(temp_file, config_file)
    
    def load_config(self):
        config_file = "config.json"
        backup_file = "config.json.bak"
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log_error(f"Config load failed: {e}")
            # Try backup
            try:
                with open(backup_file, 'r') as f:
                    return json.load(f)
            except:
                # Return factory defaults
                return self.get_factory_defaults()
```

**Model Validation:**
```python
class ModelStore:
    def save_model(self, model, path):
        # Save with checksum
        torch.save(model.state_dict(), path)
        checksum = self.calculate_checksum(path)
        with open(path + ".sha256", 'w') as f:
            f.write(checksum)
    
    def load_model(self, path):
        # Verify checksum before loading
        expected_checksum = open(path + ".sha256").read().strip()
        actual_checksum = self.calculate_checksum(path)
        
        if expected_checksum != actual_checksum:
            raise ValueError("Model checksum mismatch - corrupted file")
        
        return torch.load(path)
```

---

## 13. Power Management Design

### 13.1 Power Monitoring

**Battery Monitoring System:**
```python
class PowerManager:
    def __init__(self):
        self.voltage_pin = "AIN0"  # Analog input for voltage divider
        self.current_pin = "AIN1"  # Analog input for current sensor
        self.battery_capacity = 100  # Ah
        self.battery_voltage_nominal = 12  # V
    
    def get_voltage(self):
        """Read battery voltage via ADC"""
        raw = self.read_adc(self.voltage_pin)
        # Voltage divider: 12V -> 3.3V (R1=10k, R2=3.9k)
        voltage = raw * (13.9 / 3.9)
        return voltage
    
    def get_current(self):
        """Read current via hall effect sensor"""
        raw = self.read_adc(self.current_pin)
        # ACS712 30A sensor: 66mV/A, centered at 2.5V
        current = (raw - 2.5) / 0.066
        return current
    
    def get_state_of_charge(self):
        """Estimate battery SoC based on voltage"""
        voltage = self.get_voltage()
        
        # Lead-acid voltage-SoC curve
        if voltage >= 12.7:
            return 100
        elif voltage >= 12.4:
            return 75
        elif voltage >= 12.2:
            return 50
        elif voltage >= 12.0:
            return 25
        elif voltage >= 11.8:
            return 10
        else:
            return 0
    
    def get_power_consumption(self):
        """Calculate instantaneous power"""
        return self.get_voltage() * self.get_current()
    
    def get_estimated_runtime(self):
        """Estimate remaining runtime"""
        soc = self.get_state_of_charge()
        remaining_capacity = self.battery_capacity * (soc / 100)
        current = self.get_current()
        
        if current > 0:
            runtime_hours = remaining_capacity / current
            return runtime_hours
        else:
            return float('inf')
```

### 13.2 Power Optimization Strategies

**Dynamic Power Management:**

**Strategy 1: Adaptive Frame Rate**
```python
class AdaptivePowerManager:
    def adjust_frame_rate(self, battery_soc):
        if battery_soc > 50:
            return 30  # Full frame rate
        elif battery_soc > 25:
            return 15  # Half frame rate
        elif battery_soc > 10:
            return 5   # Minimal frame rate
        else:
            return 1   # Emergency mode
```

**Strategy 2: Camera Power Cycling**
```python
def optimize_camera_usage(self, battery_soc):
    if battery_soc > 50:
        # All cameras active
        self.enable_cameras([1, 2, 3])
    elif battery_soc > 25:
        # Primary camera only
        self.enable_cameras([1])
        self.disable_cameras([2, 3])
    else:
        # Minimal operation
        self.enable_cameras([1])
        self.set_frame_rate(1)  # 1 FPS
```

**Strategy 3: Audio Power Management**
```python
def manage_audio_power(self, battery_soc):
    if battery_soc < 10:
        # Disable audio deterrence
        self.audio_engine.disable()
        self.log_warning("Audio disabled - low battery")
    elif battery_soc < 25:
        # Reduce audio duration and volume
        self.audio_engine.set_max_duration(10)  # 10 seconds
        self.audio_engine.set_volume(50)  # 50%
```

### 13.3 Graceful Shutdown Procedure

**Shutdown Sequence:**
```python
class ShutdownManager:
    def initiate_shutdown(self, reason):
        self.log_info(f"Initiating shutdown: {reason}")
        
        # 1. Stop detection pipeline
        self.detection_pipeline.stop()
        
        # 2. Stop audio playback
        self.audio_engine.stop()
        
        # 3. Save current state
        self.state_machine.save_state()
        
        # 4. Save configuration
        self.config_manager.save_config()
        
        # 5. Flush logs
        self.logger.flush()
        
        # 6. Close camera streams
        self.camera_manager.close_all()
        
        # 7. Sync filesystem
        os.sync()
        
        # 8. Set LED to off
        self.led_controller.all_off()
        
        # 9. Power down
        os.system("shutdown -h now")
```

**Shutdown Triggers:**
- Battery SoC < 5%
- User command (*999# held for 5 seconds)
- Critical system error (after recovery attempts)
- Thermal shutdown (if temperature sensor present)

---

## 14. Security and Privacy Considerations

### 14.1 Data Security

**Local Data Protection:**
- No network connectivity = no remote attack surface
- Physical access control via enclosure lock
- Configuration password protection (optional)
- Encrypted storage for sensitive settings (optional)

**Data Retention Policy:**
- Training images: Retained indefinitely (user can delete)
- Detection logs: 30-day rolling window
- System logs: 7-day rolling window
- Model checkpoints: Keep last 3 versions

### 14.2 Privacy Considerations

**Image Data:**
- All images stored locally on device
- No transmission to external systems
- No human/face detection (animal-only)
- User responsible for data management

**Audio Data:**
- No audio recording capability
- Playback only (deterrent sounds)
- No voice recognition or processing

**Access Control:**
- Physical keypad access only
- No remote access capability
- Optional PIN code for configuration changes

### 14.3 Fail-Safe Design

**Safety Principles:**
- Audio volume limited to safe levels
- Non-lethal deterrence only
- Automatic shutdown on critical errors
- Watchdog prevents system hang
- Battery protection prevents deep discharge

---

## 15. Performance Considerations

### 15.1 Memory Management

**Memory Budget (2GB Total):**
```
Component                    Memory (MB)    Percentage
──────────────────────────────────────────────────────
OS + System Services         400            20%
TensorRT Model               200            10%
Inference Buffers            300            15%
Camera Frame Buffers         150            7.5%
Application Code             100            5%
Logging and Storage          50             2.5%
Audio Buffers                50             2.5%
Available for Training       750            37.5%
──────────────────────────────────────────────────────
Total                        2000           100%
```

**Memory Optimization:**
- Use FP16 precision (half memory)
- Limit batch size to 1 for inference
- Clear cache after each training epoch
- Use memory-mapped files for large datasets
- Implement frame buffer recycling


### 15.2 Storage Management

**Storage Layout:**
```
/findem/
├── models/
│   ├── findem_model.pt           (100 MB)
│   ├── findem_model.engine       (50 MB)
│   └── checkpoints/              (300 MB)
├── data/
│   ├── raw/                      (2 GB)
│   ├── augmented/                (10 GB)
│   ├── composite/                (5 GB)
│   └── backgrounds/              (500 MB)
├── audio/
│   ├── elephant/                 (200 MB)
│   ├── boar/                     (200 MB)
│   ├── monkey/                   (200 MB)
│   └── deer/                     (200 MB)
├── logs/
│   ├── system.log                (100 MB rolling)
│   ├── detection.db              (500 MB)
│   └── error.log                 (50 MB rolling)
└── config/
    ├── config.json               (10 KB)
    └── state.json                (10 KB)

Total: ~20 GB (64 GB SD card recommended)
```

**Storage Optimization:**
- Automatic cleanup of old augmented images after training
- Log rotation with compression
- Detection log pruning (30-day retention)
- Periodic defragmentation (if ext4)

### 15.3 Thermal Management

**Thermal Considerations:**
- Jetson Nano TDP: 10W
- Passive cooling via heatsink
- Enclosure ventilation (IP65 vents)
- Operating temperature: -10°C to 50°C

**Thermal Monitoring:**
```python
class ThermalManager:
    def __init__(self):
        self.temp_threshold_warning = 70  # °C
        self.temp_threshold_critical = 80  # °C
    
    def get_temperature(self):
        # Read from thermal zone
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read()) / 1000  # Convert to °C
        return temp
    
    def check_thermal(self):
        temp = self.get_temperature()
        
        if temp > self.temp_threshold_critical:
            self.log_error(f"Critical temperature: {temp}°C")
            self.initiate_thermal_shutdown()
        elif temp > self.temp_threshold_warning:
            self.log_warning(f"High temperature: {temp}°C")
            self.reduce_performance()
    
    def reduce_performance(self):
        # Throttle to reduce heat
        self.set_frame_rate(10)  # Reduce from 30 FPS
        self.set_cpu_governor("powersave")
```

### 15.4 Real-Time Performance

**Latency Budget:**
```
Component                    Latency (ms)    Cumulative
──────────────────────────────────────────────────────
Frame Capture                10              10
Frame Preprocessing          20              30
TensorRT Inference           80              110
Post-processing (NMS)        10              120
Detection Decision           5               125
Audio Trigger                10              135
Audio Playback Start         50              185
──────────────────────────────────────────────────────
Total Detection-to-Audio     185 ms          < 2s ✓
```

**Performance Targets:**
- Detection latency: <200ms (capture to decision)
- Audio activation: <2 seconds (requirement met)
- Frame rate: 5-10 FPS (sufficient for animal detection)
- Training time: <24 hours for 200 epochs

---

## 16. Deployment Model

### 16.1 Installation Procedure

**Pre-Installation:**
1. Site survey: Identify camera placement locations
2. Power assessment: Verify battery and solar panel sizing
3. Audio test: Verify speaker coverage area

**Installation Steps:**
1. Mount enclosure on pole or wall (2-3 meters height)
2. Install cameras with clear field of view
3. Mount speakers at elevated positions
4. Connect battery and solar panel (if used)
5. Connect all cables through weatherproof glands
6. Power on system and verify LED indicators
7. Run diagnostic test (*99#)
8. Capture training images (50-200 per class)
9. Initiate training (press START button)
10. Wait for training completion (12-24 hours)
11. Verify detection operation

**Installation Time:** 2-4 hours (excluding training)

### 16.2 Configuration Templates

**Farm Type Configurations:**

**Small Farm (1-2 hectares):**
```json
{
  "cameras": 1,
  "detection_threshold": 0.6,
  "audio_volume": 70,
  "cooldown_period": 60,
  "target_animals": ["boar", "monkey", "deer"]
}
```

**Medium Farm (2-10 hectares):**
```json
{
  "cameras": 2,
  "detection_threshold": 0.65,
  "audio_volume": 80,
  "cooldown_period": 90,
  "target_animals": ["elephant", "boar", "monkey", "deer"]
}
```

**Large Farm (>10 hectares):**
```json
{
  "cameras": 3,
  "detection_threshold": 0.7,
  "audio_volume": 90,
  "cooldown_period": 120,
  "target_animals": ["elephant", "boar", "monkey", "deer"]
}
```

### 16.3 Maintenance Schedule

**Daily:**
- Visual inspection of LED status
- Check battery voltage (*44#)

**Weekly:**
- Clean camera lenses
- Verify audio playback (*33#)
- Check detection log (*55#)

**Monthly:**
- Full diagnostic test (*99#)
- Review detection statistics
- Clean enclosure and vents
- Inspect cable connections

**Quarterly:**
- Battery capacity test
- Model retraining (if needed)
- Firmware update check (via USB)
- Replace worn components

**Annually:**
- Full system inspection
- Battery replacement (if degraded)
- Camera calibration
- Audio library update

---

## 17. Scalability and Extensibility

### 17.1 Hardware Upgrade Path

**Compute Upgrade:**
- Current: Jetson Nano 2GB
- Upgrade: Jetson Nano 4GB (2x memory)
- Future: Jetson Xavier NX (10x performance)

**Camera Expansion:**
- Current: Up to 3 cameras
- Expansion: USB hub for 4-6 cameras
- Limitation: Processing power and bandwidth

**Audio Expansion:**
- Current: 1-2 speakers
- Expansion: Multi-zone audio (4-8 speakers)
- Implementation: Audio matrix switcher

**Power Expansion:**
- Current: 100Ah battery
- Expansion: 200Ah battery bank
- Solar: 200W panel for net-positive energy

### 17.2 Software Extensibility

**Plugin Architecture:**
```python
class DetectionPlugin:
    """Base class for detection plugins"""
    def on_detection(self, detection_event):
        pass

class LoggingPlugin(DetectionPlugin):
    def on_detection(self, detection_event):
        self.log_to_database(detection_event)

class AlertPlugin(DetectionPlugin):
    def on_detection(self, detection_event):
        # Future: Send LoRa alert
        pass

class AnalyticsPlugin(DetectionPlugin):
    def on_detection(self, detection_event):
        self.update_statistics(detection_event)
```

**Model Versioning:**
- Support multiple model versions
- A/B testing capability
- Rollback to previous model
- Model performance comparison

### 17.3 Future Enhancements

**Phase 2 Features:**
- Thermal camera integration for night detection
- Multi-stage deterrence (escalation strategy)
- Adaptive learning (online model updates)
- LoRa connectivity for remote monitoring

**Phase 3 Features:**
- Multi-unit coordination (mesh network)
- Predictive analytics (animal behavior patterns)
- Integration with farm management systems
- Mobile app for configuration (optional)

---

## 18. Limitations

### 18.1 Technical Limitations

**Computational:**
- Limited to lightweight models (YOLOv5s, YOLOv7-tiny)
- Maximum 3 cameras due to processing constraints
- Frame rate limited to 5-10 FPS
- Training time 12-24 hours for typical dataset

**Memory:**
- 2GB RAM limits model complexity
- Limited training dataset size (~10GB)
- Cannot run multiple models simultaneously

**Storage:**
- 64GB limits long-term data retention
- Training data must be periodically cleaned
- Limited model checkpoint history

**Power:**
- Battery-dependent operation
- Audio usage significantly impacts runtime
- Solar charging weather-dependent

### 18.2 Environmental Limitations

**Weather:**
- Heavy rain/fog reduces camera visibility
- Dust accumulation requires regular cleaning
- Extreme temperatures may affect performance

**Lighting:**
- Night detection requires IR illumination
- Low-light conditions reduce accuracy
- Direct sunlight may cause glare

**Range:**
- Camera range limited by lens (typically 20-50m)
- Audio effective range ~100-200m
- Optimal for small to medium farms

### 18.3 Operational Limitations

**Detection:**
- Accuracy depends on training data quality
- May have false positives/negatives
- Occlusion (vegetation) reduces detection

**Deterrence:**
- Effectiveness varies by animal species
- Animals may habituate over time
- No guarantee of 100% deterrence

**Maintenance:**
- Requires periodic user intervention
- No remote diagnostics
- Field repairs may require technical expertise

---

## 19. Future Enhancements

### 19.1 Short-Term Enhancements (6-12 months)

**Enhanced Detection:**
- Multi-object tracking (track animal movement)
- Behavior analysis (grazing vs. passing through)
- Size estimation (adult vs. juvenile)

**Improved Deterrence:**
- Directional audio (aim at detected animal)
- Adaptive deterrence (escalation strategy)
- Time-of-day profiles (different sounds for day/night)

**User Experience:**
- Audio feedback for keypad commands
- More detailed LED status patterns
- USB configuration interface (connect laptop)

### 19.2 Medium-Term Enhancements (1-2 years)

**Advanced AI:**
- Transfer learning from pre-trained wildlife models
- Few-shot learning (train with fewer images)
- Anomaly detection (detect unusual behavior)

**Connectivity:**
- Optional LoRa module for remote alerts
- SMS notifications via GSM module
- Data synchronization across multiple units

**Multi-Modal Sensing:**
- Thermal camera for night detection
- Acoustic sensors for animal sounds
- PIR motion sensors for wake-on-detection

### 19.3 Long-Term Vision (2+ years)

**Intelligent Farm Protection:**
- Predictive modeling (anticipate intrusions)
- Coordinated multi-unit defense
- Integration with electric fencing
- Automated patrol (if mobile platform)

**Advanced Analytics:**
- Animal population estimation
- Migration pattern analysis
- Crop damage assessment
- ROI calculation and reporting

**Ecosystem Integration:**
- Integration with farm management systems
- Weather-aware operation
- Crop calendar integration
- Wildlife conservation data sharing

---

## Document Approval

| Role                  | Name | Signature | Date |
|-----------------------|------|-----------|------|
| System Architect      |      |           |      |
| Hardware Engineer     |      |           |      |
| Software Engineer     |      |           |      |
| AI/ML Engineer        |      |           |      |
| Product Manager       |      |           |      |

---

**End of Document**
