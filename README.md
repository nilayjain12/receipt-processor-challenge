# Receipt Processor Challenge

## Short Description
This is a Flask-based API for processing receipts and calculating points based on certain logic.

## Features
1. **Swagger API Documentation**: Comprehensive project documentation using Swagger.
2. **Docker Support**: Includes a Dockerfile for easy containerization.
3. **HTTP Error Handling**: Covers popular HTTP error codes in the project.
4. **Unit Testing**: Added unit test cases for the code.

## How to Run the Project [Environment Setup]

### Prerequisites
- Python 3.8 or higher
- Docker (optional, if you prefer to run the project in a container)

### Running the Project Locally

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/receipt-processor-challenge.git
    cd receipt-processor-challenge
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask application:**
    ```bash
    python .\app.py 
    ```

    The API will be available at `http://127.0.0.1:5000`.

### Running the Project with Docker

1. **Build the Docker image:**
    ```bash
    docker build -t receipt-processor-challenge .
    ```

2. **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 receipt-processor-challenge
    ```

    The API will be available at `http://127.0.0.1:5000`.

## API Documentation

For detailed API documentation, visit the Swagger UI at `http://127.0.0.1:5000/apidocs`.

## Example Usage

### Submit a Receipt for Processing
```bash
curl -X POST "http://127.0.0.1:5000/receipts/process" -H "Content-Type: application/json" -d '{
    "retailer": "M&M Corner Market",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
        {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}
    ],
    "total": "6.49"
}'
```

## Testing the API with Postman
### **Step-by-Step Guide**
1. **Open Postman**: If you don’t have Postman installed, download and install it from Postman's official website.

2. **Create a New Request**: Click on the “New” button and then select “Request”.

3. **Set Request URL**:

    - **For Processing a Receipt**:
    - **Method**: POST
    - **URL**: http://127.0.0.1:5000/receipts/process
    - **Body**: Select raw and JSON, then paste the following:
        ```
        {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {"shortDescription": "Mountain Dew 12PK", "price": "6.49"}
        ],
        "total": "6.49"
        }
        ```
4. **Send the Request**: Click the “Send” button and check the response.

5. **Get Points for a Receipt**:

    - **Method**: GET
    - **URL**: http://127.0.0.1:5000/receipts/{id}/points
    - Replace {id} with the actual receipt ID returned from the previous POST request.

6. **Check the Response**: The response will show the points awarded for the receipt.

## Running Unit Tests
Run the tests using the command:<br>
```
python -m unittest test_app.py
```