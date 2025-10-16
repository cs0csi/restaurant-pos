# Restaurant POS API

This is the backend for the Restaurant POS system.

## Running the Application

To run the application locally, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the application:**
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```

    For local development, it's recommended to run without the `DATABASE_URL` environment variable set. The application will fall back to a local SQLite database at `/tmp/test.db`.

## Running the Automated Tests

This project includes a suite of automated tests to verify the functionality of the API.

1.  **Install dependencies:**
    Make sure you have all the required packages, including the testing libraries:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the application:**
    The tests require the application to be running. You can start it with the following command:
    ```bash
    export DATABASE_URL="sqlite:////tmp/test.db" && uvicorn main:app --host 0.0.0.0 --port 8000 &
    ```

3.  **Run the tests:**
    Navigate to the `backend` directory and run `pytest`:
    ```bash
    pytest
    ```