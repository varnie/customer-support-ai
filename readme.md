# Support Ticket Processing System

This project is designed to automate the processing of support tickets using AI models to categorize, prioritize, and generate initial responses. It integrates with OpenAI and Anthropic AI services to analyze ticket content and provide actionable insights, streamlining the support process.

## Features

- **Ticket Submission**: Users can submit tickets via a REST API.
- **Automatic Ticket Processing**: Tickets are automatically categorized, prioritized, and assigned an initial response using AI models.
- **Manual Ticket Processing Trigger**: A manual trigger is available to process all unprocessed tickets.
- **Database Integration**: PostgreSQL for ticket storage and Redis for job queue management.
- **Docker Support**: The application is containerized for easy deployment and scaling.

## Technologies Used

- **Python**: Primary programming language.
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **Alembic**: Database migrations.
- **Redis & RQ**: For job queue management.
- **Docker**: Containerization and deployment.
- **OpenAI & Anthropic**: AI services for processing tickets.

## Getting Started

### Prerequisites

- Docker and Docker Compose installed on your machine.
- An API key from OpenAI and Anthropic for AI model access.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/varnie/customer-support-ai.git
   
2. Navigate to the project directory:  <pre>cd support-ticket-system </pre>

3. Copy the .env.example file to .env and fill in your API keys and database credentials:  <pre>cp .env.example .env </pre>

4. Build containers:  <pre>make build</pre>

5. Apply the database migrations:  <pre>make db-upgrade</pre>

6. Start the application:  <pre>make up</pre>

### Usage
Submit a Ticket:  <pre>curl -X POST http://localhost:8000/ticket \ -H "Content-Type: application/json" \ -d "{\"subject\": \"Your Subject\", \"body\": \"Your Ticket Body\", \"customer_email\": \"user@example.com\"}" </pre>
List All Tickets:  <pre>curl -X GET http://localhost:8000/tickets </pre>
Process Tickets Manually:  <pre>curl -X POST http://localhost:8000/process </pre>


### Testing
Run the tests using the following command:  <pre>make test</pre>


### Contributing
Contributions are welcome! Please feel free to submit a pull request. 
