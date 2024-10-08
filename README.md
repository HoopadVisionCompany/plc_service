

# PLC Service


## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

Make sure you have Python and `virtualenv` installed on your machine.

### 1. Set Up Virtual Environment

Create a virtual environment to isolate dependencies:

```bash
virtualenv venv
```

Activate the virtual environment:

```bash
source venv/bin/activate
```

### 2. Install Dependencies

Install the required dependencies:

```bash
pip install -r req.txt
```

### 3. Configure Environment Variables

Before running the project, configure the `.env` file.

#### 3.1 Create the `.env` File

Copy the `.env.example` file to create your `.env` file:

```bash
cp .env.example .env
```

#### 3.2 Set Uvicorn Host and Port

Define the `UVICORN_HOST` and `UVICORN_PORT` in the `.env` file:

```bash
UVICORN_HOST="localhost"  # Host for Uvicorn
UVICORN_PORT=9091         # Port for Uvicorn
```

#### 3.3 Set MongoDB URL and Database Name

Define the `MONGODB_URL` and `DB_NAME` in the `.env` file:

```bash
MONGODB_URL="mongodb://localhost:27017"  # MongoDB connection URL
DB_NAME="gateservice"                    # Main database name
```

#### 3.4 Use Test Database Option

To switch between the test and main database, use the `USE_TEST_DB` variable. If set to `True`, the application will use the test database specified by `TEST_DB_NAME`.

```bash
USE_TEST_DB=True              # Set to True to use test database
TEST_DB_NAME="test_gateservice"  # Name of the test database
```

Ensure that the appropriate database is selected based on your environment (test or production).

### 4. Run the Application

To run the FastAPI application, execute the following command:

```bash
python main.py --all
```
