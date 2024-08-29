
# Parking Management System

## Description

Parking Management System is an application that helps users manage their parking spaces.

## Features

- User authentication: Users can create accounts, log in, and log out.
- Online payment: Users can make online payments using credit card.
- AI license plate detection: detects license plates and automatically starts a parking session.
- Parking story: Users can see their parking story.
- Payment history: Users can see their payment history.


## Technologies Used

- Python
- FastAPI
- PostgreSQL (for the database)
- Docker (for containerization)
- Other dependencies listed in `requirements.txt` and `package.json`

## Installation

To run the Photo Share project locally, follow these steps:

1. Clone the repository:
   ```sh
   git clone https://github.com/rusetskiy1974/DataScience_project
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Create file `.env` using `.env.sample`.


3. Set up the database:
   - Run `docker-compose up --build` to create Docker container.
   - Create a PostgreSQL database named `parking_manager` or other name that you put in your `.env` file.
   - Run `alembic upgrade head` to install migration in DB.
   

4. Access the application at `http://localhost:8000` or `127.0.0.1:8000` in your web browser.

## Usage

1. Register for an account.
2. Log in with your credentials.
3. Make credit payment on your account.
4. Go to parking and wait for your car's license plate to be recognized.
5. Enjoy your parking.

## API Documentation

The API documentation for the Photo Share project is available at `http://localhost:8000/docs` or `http://127.0.0.1:8000/docs#/` when the application is running.

## Contributing

Contributions to Photo Share are welcome! To contribute, please follow these guidelines:
- Fork the repository
- Create a new branch (`git checkout -b feature`)
- Make your changes
- Commit your changes (`git commit -am 'Add new feature'`)
- Push to the branch (`git push origin feature`)
- Create a new Pull Request
