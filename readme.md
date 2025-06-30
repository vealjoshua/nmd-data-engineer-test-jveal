## New Math Data Assessment

This project implements a data processing pipeline using AWS Lambda and S3 to analyze orders data.

### Prerequisites

- Python 3.8+
- Terraform 1.0+
- Docker
- AWS CLI configured with appropriate credentials

### Setup and Testing

1. **Run Unit Tests**
   ```bash
   # Run all tests
   python -m unittest discover -s tests
   
   # Run specific test file
   python tests/test_lambda_function.py
   python tests/test_orders_analytics.py
   ```

2. **Build Docker Image**
   ```bash
   # Build the Docker image
   docker build -t nmd-data-lambda .
   ```

### Infrastructure Deployment

1. **Initialize Terraform**
   ```bash
   cd terraform
   terraform init
   ```

2. **Plan and Apply Changes**
   ```bash
   terraform plan
   terraform apply
   ```

3. **Verify Deployment**
   ```bash
   terraform show
   ```

### Local Development

1. **Run Lambda Function Locally**
   ```bash
   # Ensure you have the required Python packages installed
   pip install -r requirements.txt
   
   # Test the Lambda function
   python app/lambda_function.py test_event.json
   ```

2. **Test Analytics Functions**
   ```bash
   # Test individual analytics functions
   python -m unittest tests/test_orders_analytics.py
   ```

### Project Structure

```
.
├── app/                      # Lambda function code
│   ├── lambda_function.py    # Main Lambda handler
│   └── orders_analytics.py   # Data analytics functions
├── terraform/               # Infrastructure as Code
├── tests/                   # Unit tests
│   ├── test_lambda_function.py
│   └── test_orders_analytics.py
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Error Handling

The system implements robust error handling for:
- Empty CSV files
- Invalid CSV format
- S3 errors
- Missing required columns

### Contributing

1. Run tests before committing changes
2. Update documentation as needed
3. Follow Python best practices
4. Add appropriate error handling

### License

This project is proprietary to New Math Data and is not open source.
