# Use an official Python image as the base
FROM public.ecr.aws/lambda/python:3.12

# Copy requirements.txt first
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the app code
COPY ./app ${LAMBDA_TASK_ROOT}

# Set the default command to run when the container starts
CMD ["lambda.lambda_handler"]