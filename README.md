# AeroLogistics: Intelligent Drone Fleet Management System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![AI](https://img.shields.io/badge/AI-Scikit--Learn-orange.svg)
![FastAPI](https://img.shields.io/badge/Edge_Computing-FastAPI-009688.svg)
![Coverage](https://img.shields.io/badge/Tests-Passing-green)

> **A hybrid Desktop/Edge architecture for autonomous logistics, featuring AI-driven predictive maintenance, real-time environmental telemetry, and concurrent mission scheduling.**

## Overview

AeroLogistics is a comprehensive control station designed to simulate and manage high-frequency drone delivery operations. Unlike standard CRUD applications, this system integrates **physics-based energy modeling** and **machine learning** to make safety-critical decisions in real-time.

The system operates on a **Local-First** architecture (Tkinter) for high-availability warehouse control, paired with a **Headless Edge Server** (FastAPI) for remote monitoring via mobile devices.

---

## System Architecture

The project follows a strict **Layered Architecture** utilizing **Dependency Injection** to decouple business logic from data persistence and external APIs.

```mermaid
graph TD
    User[User / Logistics Manager] --> UI[Desktop UI (Tkinter)]
    Mobile[Mobile Device] --> API[Edge API (FastAPI)]
    
    subgraph Core_Application
        UI --> Service[Logistic Service Layer]
        API --> Service
        
        Service --> AI[AI Prediction Engine]
        Service --> Weather[Weather API Service]
        Service --> Repo[Repository Layer]
        
        Repo --> DB[(SQLite Database)]
    end
    
    subgraph Background_Threads
        Scheduler[Mission Scheduler]
        Charger[Auto-Charging System]
        Server[Uvicorn Server]
    end
    
    Scheduler -.-> Service
    Charger -.-> Repo
    Server -.-> API
```

---

## Key Features

1. Intelligent Dispatch & Physics Engine
The system does not simply "assign" drones. It performs a feasibility simulation for every mission request:

Dynamic Battery Calculation: Uses a payload-to-capacity ratio formula. A 5kg package drains more battery on a small drone than a heavy-lift drone.

Environmental Awareness: Connects to the OpenWeatherMap 5-Day Forecast API. Missions scheduled for the future are validated against the predicted weather for that specific hour.

AI-Powered Penalties: A Linear Regression Model (scikit-learn) predicts battery degradation based on wind speed, temperature, and precipitation.

2. Concurrency & Threading
Non-Blocking UI: The GUI remains responsive while heavy tasks run in the background.

Autonomous Scheduler: A daemon thread monitors scheduled missions and auto-deploys drones when the start time matches the system clock.

Smart Charging System: An independent thread monitors idle drones and trickle-charges them, writing updates to the database safely using thread locks.

3. Edge Computing & Mobile Dashboard
A lightweight FastAPI server runs in a background thread, serving a Server-Side Rendered (SSR) HTML dashboard.

Allows warehouse staff to view live drone telemetry (Battery, Status, Location) from smartphones.

Implements Auto-Refresh logic for near-real-time monitoring.

---

## The AI & Math Model

The system rejects missions using the following logic:

**Total Drain = (distance / 600) * (1 + Load Factor) * AI Weather Multiplier**

Load Factor = Drone Max Payload / Parcel Weight

AI Multiplier: A trained model that outputs 1.0 (Perfect conditions) to 1.5+ (Storm/Freezing).

--- 

## Tech Stack

| Component | Technology | Use Case |
| :--- | :--- | :--- |
| **Language** | Python 3.11 | Core Logic |
| **Desktop UI** | Tkinter / CustomTkinter | Warehouse Control Station |
| **Mobile API** | FastAPI + Uvicorn | Remote Edge Monitoring |
| **Database** | SQLite3 | Local Persistence |
| **AI / ML** | Scikit-Learn | Battery Degradation Modeling |
| **External API** | OpenWeatherMap | Real-time & Forecast Telemetry |
| **Testing** | Unittest + Mock | Unit & Integration Testing |

---

## Screenshots

! [Screenshot1](Screenshots/Screenshot1.png)
! [Screenshot2](Screenshots/Screenshot2.png)
! [Screenshot3](Screenshots/Screenshot3.png)
! [Screenshot4](Screenshots/Screenshot4.png)
! [Screenshot5](Screenshots/Screenshot5.png)
! [Screenshot6](Screenshots/Screenshot6.png)
! [Screenshot7](Screenshots/Screenshot7.png)

---

## Installation & Setup

1. **Clone the Repository**
    ``git clone https://github.com/yourusername/aerologistics.git``

2. **Configure Environment**
- Create a settings.properties file:
[settings]
weather_api_key = YOUR_OPENWEATHERMAP_KEY
weather_city = City you want

3. **Run the system**
Use: `python main.py`

4. **Access Mobile Dashboard**

    Open your browser to: http://localhost:8000/drones

## Building Executable

To compile the application into a standalone Windows `.exe` file, use **PyInstaller**.

1.  **Install PyInstaller**
    ```bash
    pip install pyinstaller
    ```

2.  **Build the Application**
    Run the following command in the project root. This bundles the FastAPI server, UI, and ML models into a single file and attaches the custom icon.
    ```bash
    pyinstaller --name="AeroLogistics" --onefile --noconsole --icon=app_icon.ico --hidden-import=uvicorn --hidden-import=fastapi --hidden-import=sklearn --hidden-import=pandas main.py
    ```

3.  **Post-Build Setup**
    The executable will appear in the `dist/` folder. **Crucial:** You must manually copy the `settings.properties` file into the `dist/` folder for the application to run correctly.

## Testing

The project includes a robust suite of unit tests using unittest.mock to validate the physics engine without requiring real API calls.

Use : ``python test_suite.py`` to run the tests

**Key Test Cases Covered:**

``test_assign_mission_rejection_long_distance:`` Validates physics constraints (e.g., rejecting a 66km flight).

``test_ai_weather_penalty:`` Verifies that storms increase calculated battery cost.

``test_concurrency:`` Ensures charging threads do not lock the database.

---

## Future Roadmap

[] Containerization: Docker support for easy deployment on Raspberry Pi (Edge Device).

[] Visual Route Planning: Integration with Mapbox Static API to show flight paths.

[] Predictive Maintenance: Using historical flight logs to predict motor failure before it happens.

---

**Author:** [Garbovan Alex-Razvan](https://github.com/AlexRazvan19)
**Contact:** [Email](mailto:garbovanrazvan5@gmail.com) | [LinkedIn Profile](https://www.linkedin.com/in/alex-garbovan/)
