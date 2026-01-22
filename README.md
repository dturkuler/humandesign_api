# Human Design API

Welcome to the Human Design API! This project provides a robust and scalable API for calculating various Human Design features based on birth data. Built with FastAPI and leveraging powerful astrological and geographical libraries, it offers a comprehensive solution for integrating Human Design analytics into your applications.

## Project Overview
 
The **Human Design API** is a high-performance Python service meant to power modern Human Design applications. It serves as a comprehensive backend engine that:

1.   **Calculates** core and deep Human Design metrics from birth data (Earth, Moon, Nodes, Planets, Gates, Lines, Color, Tone, Base).
2.  **Resolves** birth locations to precise geocoordinates and timezones automatically.
3.  **Visualizes** results by generating beautiful, high-quality BodyGraph images on-the-fly.

Whether you are building a mobile app, a professional dashboard, or a personal research tool, this API provides the rigorous astrological data and visual assets you need, all containerized for easy deployment.

### Key Features:

*   **V2 Calculate API (NEW)**: High-performance `POST /v2/calculate` with semantic enrichment, Dream Rave, and Global Cycle support.
*   **High-Fidelity Maia Matrix v2**: Advanced relational analysis with planetary triggers, nodal resonance, and sub-circuit details.
*   **Penta Analysis 2.0**: Enhanced Group Dynamics (3-5 people) via the `/analyze/penta` endpoint, providing high-level semantic analysis (Sovereign Standard).
*   **Maia-Penta Hybrid Analysis**: Flagship `POST /analyze/maia-penta` endpoint for professional composite + group dynamics in a single request.
*   **Grounded 10x Interpretation**: Consultant-grade psychology-grounded reports with zero-jargon semantic output.
*   **Global Performance (Sub-20ms)**: Integrated `TimezoneFinder` Singleton and geocoding bypass to achieve 100x lower latency.
*   **Coordinate Support**: All endpoints now support optional `latitude` and `longitude` parameters to bypass geocoding services for maximum precision and speed.
*   **FastAPI Backend**: High-performance, async-ready Python web framework.
*   **Precise Calculations**: Uses `pyswisseph` for Swiss Ephemeris accuracy and `geopy`/`timezonefinder` for reliable location and timezone resolution.
*   **BodyGraph Visualization**: Generates high-fidelity, transparent BodyGraph charts in PNG, SVG, and JPG formats via the `/bodygraph` endpoint.
*   **Detailed Pairwise Analysis**: Calculates granular relationship details (new/duplicated channels) for exactly two people via the `/analyze/composite` endpoint.
*   **Transit Analysis**: Provides Daily Weather and Solar Return (Yearly Theme) calculations for advanced forecasting.
*   **Comprehensive Chart Data**: Returns Energy Type, Strategy, Authority, Profile, Incarnation Cross, Variables, Age, Western Zodiac Sign, and full Planetary/Gate positions.
*   **Network-Independent Tests**: Optimized geocoding bypass to ensure 100% deterministic and fast verification.

## Installation and Setup

To get the Human Design API up and running, follow these steps:

### Prerequisites

*   **Docker**: Ensure Docker is installed and running on your system. You can download it from [Docker's official website](https://www.docker.com/products/docker-desktop).
*   **Docker Compose**: Docker Compose is usually bundled with Docker Desktop. Verify its installation by running `docker-compose --version` in your terminal.

### Steps

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/humandesign_api.git
    cd humandesign_api
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory of the project based on the `.env_example` file. This file will store your API token.

    ```
    HD_API_TOKEN=your_secret_token_here
    ```
    Replace `your_secret_token_here` with a strong, unique token.

3.  **Build and Run with Docker Compose**:
    Navigate to the project root directory in your terminal and run:

    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: This flag tells Docker Compose to build the images before starting containers. This is necessary for the first run or after any changes to the `Dockerfile` or `requirements.txt`.
    *   `-d`: This flag runs the containers in detached mode, meaning they will run in the background.

4.  **Verify Installation**:
    Once the containers are up, the API should be accessible at `http://localhost:9021`. You can verify its status by checking your Docker Desktop dashboard or by running:

    ```bash
    docker ps
    ```
    You should see a container named `humandesignapi` running.

## Folder Structure
 
The project is organized as follows:
 
```
.
├── .env_example
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
├── docker-compose.yml
├── Dockerfile
├── openapi.yaml
├── requirements.txt
├── pyproject.toml
└── src/
    └── humandesign/
        ├── api.py           # FastAPI Application Entry
        ├── data/            # Static layout and hd data
        ├── features/        # Core Rave Engine logic
        ├── routers/         # API Route definitions
        ├── schemas/         # Pydantic validation models
        ├── services/        # Business logic services
        └── utils/           # Utilities (Astrology, Versioning, etc.)
```
 
*   **`src/humandesign/api.py`**: The main FastAPI application. Defines endpoints, handles requests, and integrates calculation and visualization logic.
*   **`chart.py`**:  Generates high-fidelity BodyGraph images (PNG, SVG, JPG) using `matplotlib` and extracted vector geometry.
*   **`composite_handler.py`**: Encapsulates logic for composite chart calculations, including input processing and feature enrichment.
*   **`convertJSON.py`**: Utility functions for formatting calculation results into structured JSON.
*   **`docker-compose.yml`**: Orchestrates the Docker service for easy deployment.
*   **`Dockerfile`**: Defines the container environment for the API.
*   **`geocode.py`**: Handles geocoding and timezone resolution.
*   **`hd_constants.py`**: Stores Human Design constants, mappings, and databases.
*   **`hd_features.py`**: Core logic for Human Design astrological calculations.
*   **`layout_data.json`**: Contains precise SVG paths and coordinates for rendering the BodyGraph.
*   **`openapi.yaml`**: The OpenAPI 3.0 specification file for the API.
*   **`requirements.txt`**: Python dependencies.
*   **`pyproject.toml`**: Standard configuration file for project metadata and dependencies, including the single source of truth for the project version.
*   **`CHANGELOG.md`**: Records all notable changes to the project.
*   **`LICENSE`**: Project license.
*   **`README.md`**: Project documentation (this file).
*   **`.env_example`**: Template for environment variables.
*   **`static/`**: Static assets directory.

## API Usage
 
 The Human Design API provides several powerful endpoints for analysis and visualization.
 
 ### 1. `GET /calculate`
 
 Calculates comprehensive Human Design features based on birth information.
 
 #### Parameters
 
 | Name     | Type    | Description                                     | Required |
 | :------- | :------ | :---------------------------------------------- | :------- |
 | `year`   | `integer` | Birth year (e.g., `1990`)                       | Yes      |
 | `month`  | `integer` | Birth month (e.g., `7` for July)                | Yes      |
 | `day`    | `integer` | Birth day (e.g., `15`)                          | Yes      |
 | `hour`   | `integer` | Birth hour (24-hour format, e.g., `14` for 2 PM) | Yes      |
 | `minute` | `integer` | Birth minute (e.g., `30`)                       | Yes      |
 | `second` | `integer` | Birth second (optional, default `0`)            | No       |
 | `place`  | `string`  | Birth place (city, country, e.g., `London, UK`) | Yes      |
 
 #### Example Request
 
 ```bash
 curl -X GET "http://localhost:9021/calculate?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK" \
      -H "Authorization: Bearer your_secret_token_here"
 ```
 
 #### Example Response (Condensed)
 ```json
 {
   "general": {
     "birth_date": "1990-07-15T13:30:00Z",
     "age": 35,
     "gender": "male",
     "islive": true,
     "zodiac_sign": "Cancer",
     "energy_type": "Projector",
     "strategy": "Wait for the Invitation",
     "inner_authority": "Solar Plexus",
     "inc_cross": "The Right Angle Cross of the Maya (2)",
     "profile": "3/5: Martyr Heretic",
     "definition": "Split Definition",
     ...
   },
   "gates": { ... },
   "channels": {
     "Channels": [
       { "channel": "30/41: The Channel of Recognition..." }
     ]
   }
 }
 ```
 
 ---
 
 ### 2. `GET /bodygraph`
 
 Generates a visual BodyGraph chart image based on birth information.
 
 #### Parameters
 Accepts the same birth parameters as `/calculate` (year, month, day, hour, minute, second, place) plus:
 
 | Name   | Type   | Description                                          | Default |
 | :----- | :----- | :--------------------------------------------------- | :------ |
 | `fmt`  | `string` | Image format: `png`, `svg`, `jpg`, `jpeg`          | `png`   |
 
 #### Example Request
 ```bash
 curl -X GET "http://localhost:9021/bodygraph?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&fmt=png" \
      -H "Authorization: Bearer your_secret_token_here" \
      -o bodygraph.png
 ```
 <img src="src/humandesign/static/bodygraph_sample.png" alt="alt text" width="50%" />



 ---
 
 ### 3. `GET /transits/daily`
 
 Calculates the "Weather of the Day" by creating a composite chart of the user's birth data and the current planetary transit.
 
 #### Parameters
 Requires **Birth Data** (year...place) plus:
 
 | Name           | Type    | Description                   | Required |
 | :------------- | :------ | :---------------------------- | :------- |
 | `transit_year` | `integer` | Year of the transit           | Yes      |
 | `transit_month`| `integer` | Month of the transit          | Yes      |
 | `transit_day`  | `integer` | Day of the transit            | Yes      |
 
 #### Example Request
 ```bash
 curl -X GET "http://localhost:9021/transits/daily?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&transit_year=2025&transit_month=12&transit_day=22" \
      -H "Authorization: Bearer your_secret_token_here"
 ```
 
 ---
 
 ### 4. `GET /transits/solar_return`
 
 Calculates the "Yearly Theme" (Solar Return Analysis).
 
 #### Parameters
 Requires **Birth Data** (year...place) plus:
 
 | Name             | Type    | Description                                      | Default |
 | :--------------- | :------ | :----------------------------------------------- | :------ |
 | `sr_year_offset` | `integer` | Years after birth (e.g. `0`=Current SR, `1`=Next)| `0`     |
 
 #### Example Request
 ```bash
 curl -X GET "http://localhost:9021/transits/solar_return?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&sr_year_offset=0" \
      -H "Authorization: Bearer your_secret_token_here"
 ```
 
 ---
 
 ### 5. `POST /analyze/composite`
 
 Calculates detailed pairwise composite analysis for exactly two people.
 
 #### Request Body
 ```json
 {
   "person1": { "place": "Berlin, Germany", "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30 },
   "person2": { "place": "Munich, Germany", "year": 1988, "month": 11, "day": 22, "hour": 9, "minute": 15 }
 }
 ```
 
 #### Example Request
 ```bash
 curl -X POST "http://localhost:9021/analyze/composite" \
      -H "Authorization: Bearer your_secret_token_here" \
      -H "Content-Type: application/json" \
      -d @payload.json
 ```
 
 #### Response
 ```json
 {
   "participants": ["person1", "person2"],
   "new_channels": [
     { "gate": 59, "ch_gate": 6, "meaning": ["Mating", "A d. focused on reproduction"] }
   ],
   "duplicated_channels": [],
   "new_chakras": ["SolarPlexus"],
   "composite_chakras": ["Ajna", "Throat", "G_Center", "SolarPlexus", "Sacral", "Root"]
 }
 ```
 
 ---
 
 ### 6. `POST /analyze/compmatrix`
 
 Calculates the composite Human Design matrix (Relationship Mechanics) for two or more people.
 
 #### Request Body
 ```json
 {
   "person1": { "place": "Berlin, Germany", "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30 },
   "person2": { "place": "Munich, Germany", "year": 1988, "month": 11, "day": 22, "hour": 9, "minute": 15 }
 }
 ```
 
 #### Example Request
 ```bash
 curl -X POST "http://localhost:9021/analyze/compmatrix" \
      -H "Authorization: Bearer your_secret_token_here" \
      -H "Content-Type: application/json" \
      -d @payload.json
 ```
 
 ---
 
 ### 7. `POST /analyze/penta`
 
 Calculates the **Group Dynamics (Penta)** using the Sovereign Standard (Consultant-Level Interpretation).
 
 #### Request Body
 ```json
 {
   "group_type": "family", // or "business"
   "participants": {
     "Person A": { "place": "City, Country", "year": 1985, "month": 6, "day": 15, "hour": 14, "minute": 30 },
     "Person B": { ... }
   }
 }
 ```
 
 #### Example Request
 ```bash
 curl -X POST "http://localhost:9021/analyze/penta" \
      -H "Authorization: Bearer your_secret_token_here" \
      -H "Content-Type: application/json" \
      -d @penta_v2_payload.json
 ```
 
 #### Response
 ```json
 {
   "functional_roles": { "Planning": ["Person A"] },
   "penta_anatomy": {
     "upper_penta": {
       "channels": {
         "31-7": {
           "business_label": "Administration & Planning",
           "contributors": {
             "Person A": {
               "gate_31": { "lines": [6], "line_labels": ["Administrator (Objective)"] }
             }
           }
         }
       }
     }
   }
 }
 ```

 ---
 
 ## API Documentation
 
 For comprehensive details, industrial-standard references, and runnable examples, please refer to the [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) file.
 
 The project includes an OpenAPI 3.0 specification file named `openapi.yaml`. This file describes the API endpoints, request parameters, responses, and schemas in a standard format.
 
 ### Using `openapi.yaml`
 
 You can use the `openapi.yaml` file to:

1.  **Visualize the API**:
    *   **VS Code**: Install extensions like "Swagger Viewer" or "OpenAPI (Swagger) Editor" to preview the API documentation directly in your editor.
    *   **Online Viewers**: Copy the content of `openapi.yaml` and paste it into the [Swagger Editor](https://editor.swagger.io/) to view and interact with the API documentation.

2.  **Import into Postman**:
    *   Open Postman.
    *   Click on the **Import** button in the top left corner.
    *   Drag and drop the `openapi.yaml` file or select it from your file system.
    *   Postman will automatically generate a collection with the request (including examples) pre-configured.

3.  **Generate Client Libraries**:
    *   Tools like `openapi-generator` can use this file to generate API client code for various programming languages (e.g., Python, JavaScript, Java).

---
*Documentation generated for Human Design API v3.4.0*


