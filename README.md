# Human Design API

Welcome to the Human Design API! This project provides a robust and scalable API for calculating various Human Design features based on birth data. Built with FastAPI and leveraging powerful astrological and geographical libraries, it offers a comprehensive solution for integrating Human Design analytics into your applications.

## Project Overview

The Human Design API is a Python-based service designed to compute intricate Human Design charts. It takes birth details (year, month, day, hour, minute, second, and place) as input and returns a detailed JSON response including energy type, inner authority, incarnation cross, profile, active/inactive chakras, split definition, and planetary gate information.

The API is containerized using Docker, ensuring consistent and isolated environments for development and deployment. Docker Compose is used for easy orchestration of the API service.

### Key Features:

*   **FastAPI Backend**: High-performance Python web framework for building APIs.
*   **Human Design Calculations**: Utilizes `pyswisseph` for precise astrological calculations and `geopy` for geocoding and timezone determination.
*   **Comprehensive Output**: Provides detailed Human Design chart information, including energy type, inner authority, incarnation cross, profile, active/inactive chakras, split definition, and planetary gate data.
*   **Dockerized Deployment**: Easy to set up and deploy using Docker and Docker Compose.
*   **Authentication**: API token-based authentication for secure access.

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
├── api.py
├── chart.py
├── convertJSON.py
├── docker-compose.yml
├── Dockerfile
├── geocode.py
├── hd_constants.py
├── hd_features.py
├── layout_data.json
├── openapi.yaml
├── requirements.txt
├── static/
│   └── favicon.ico
└── version.py
```

*   **`api.py`**: The main FastAPI application. Defines endpoints, handles requests, and integrates calculation and visualization logic.
*   **`chart.py`**:  Generates high-fidelity BodyGraph images (PNG, SVG, JPG) using `matplotlib` and extracted vector geometry.
*   **`convertJSON.py`**: Utility functions for formatting calculation results into structured JSON.
*   **`docker-compose.yml`**: Orchestrates the Docker service for easy deployment.
*   **`Dockerfile`**: Defines the container environment for the API.
*   **`geocode.py`**: Handles geocoding and timezone resolution.
*   **`hd_constants.py`**: Stores Human Design constants, mappings, and databases.
*   **`hd_features.py`**: Core logic for Human Design astrological calculations.
*   **`layout_data.json`**: Contains precise SVG paths and coordinates for rendering the BodyGraph.
*   **`openapi.yaml`**: The OpenAPI 3.0 specification file for the API.
*   **`requirements.txt`**: Python dependencies.
*   **`version.py`**: Single source of truth for the project version.
*   **`CHANGELOG.md`**: Records all notable changes to the project.
*   **`LICENSE`**: Project license.
*   **`README.md`**: Project documentation (this file).
*   **`.env_example`**: Template for environment variables.
*   **`static/`**: Static assets directory.

## API Usage

The Human Design API provides a single endpoint for calculating Human Design features.

### `GET /calculate`

Calculates Human Design features based on birth information.

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

#### Authentication

This endpoint requires an API token passed in the `Authorization` header as a Bearer token.

`Authorization: Bearer your_secret_token_here`

#### Example Request

```bash
curl -X GET "http://localhost:9021/calculate?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK" \
     -H "Authorization: Bearer your_secret_token_here"
```

### `GET /bodygraph`

Generates a visual BodyGraph chart image based on birth information.

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
| `fmt`    | `string`  | Image format: `png`, `svg`, `jpg`, `jpeg` (default: `png`) | No       |

#### Authentication

This endpoint requires an API token passed in the `Authorization` header as a Bearer token.

`Authorization: Bearer your_secret_token_here`

#### Example Request

```bash
curl -X GET "http://localhost:9021/bodygraph?year=1990&month=7&day=15&hour=14&minute=30&place=London%2C%20UK&fmt=png" \
     -H "Authorization: Bearer your_secret_token_here" \
     -o bodygraph.png
```

#### Response

Returns the image file directly (MIME type `image/png`, `image/svg+xml`, or `image/jpeg`).

![BodyGraph Sample](static/bodygraph_sample.png)

#### Example Response

```json
{
  "general": {
    "birth_date": "(1990, 7, 15, 14, 30, 0)",
    "create_date": "(1990, 4, 20, 17, 2, 20.0)",
    "energie_type": "MANIFESTING GENERATOR",
    "inner_authority": "Sacral",
    "inc_cross": "The Right Angle Cross of the Sleeping Phoenix (2)",
    "profile": "2/4: Hermit Opportunist",
    "defined_centers": [
      "Head",
      "Ajna",
      "Throat",
      "G_Center",
      "Sacral",
      "Spleen",
      "Root"
    ],
    "undefined_centers": [
      "SolarPlexus",
      "Heart"
    ],
    "split": "Split Definition",
    "variables": {
      "right_up": "right",
      "right_down": "left",
      "left_up": "right",
      "left_down": "right"
    }
  },
  "gates": {
    "prs": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 120.98,
          "Gate": 20,
          "Line": 2,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "Earth",
          "Lon": 300.98,
          "Gate": 34,
          "Line": 2,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Moon",
          "Lon": 270.0,
          "Gate": 58,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "North_Node",
          "Lon": 29.0,
          "Gate": 49,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "South_Node",
          "Lon": 209.0,
          "Gate": 4,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mercury",
          "Lon": 100.0,
          "Gate": 16,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 110.0,
          "Gate": 35,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mars",
          "Lon": 180.0,
          "Gate": 13,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Jupiter",
          "Lon": 250.0,
          "Gate": 30,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Saturn",
          "Lon": 330.0,
          "Gate": 41,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 50.0,
          "Gate": 25,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Neptune",
          "Lon": 70.0,
          "Gate": 17,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 90.0,
          "Gate": 21,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        }
      ]
    },
    "des": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 300.98,
          "Gate": 34,
          "Line": 4,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Earth",
          "Lon": 120.98,
          "Gate": 20,
          "Line": 4,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "Moon",
          "Lon": 270.0,
          "Gate": 58,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "North_Node",
          "Lon": 29.0,
          "Gate": 49,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "South_Node",
          "Lon": 209.0,
          "Gate": 4,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mercury",
          "Lon": 100.0,
          "Gate": 16,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 110.0,
          "Gate": 35,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mars",
          "Lon": 180.0,
          "Gate": 13,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Jupiter",
          "Lon": 250.0,
          "Gate": 30,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Saturn",
          "Lon": 330.0,
          "Gate": 41,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 50.0,
          "Gate": 25,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Neptune",
          "Lon": 70.0,
          "Gate": 17,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 90.0,
          "Gate": 21,
          "Line": 1,
          "Color": 1,
          "Tone": 1,
          "Base": 4,
          "Ch_Gate": 0
        }
      ]
    }
  },
  "channels": {
    "Channels": [
      {
        "channel": "20/34: The Channel of Charisma (A Design of Thoughts Becoming Deeds)"
      },
      {
        "channel": "20/57: The Channel of the Brainwave (A Design of Penetrating Awareness)"
      }
    ]
  }
}
```

## API Documentation

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

