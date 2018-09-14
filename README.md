# Tradecore

Basic social media prototype application, featuring basic functionality APIs of sign-up, login, logout, creating posts and liking/disliking them. Project built using [Django framework](https://github.com/django/django) on Python 3.6.

## Features
- Sign up and login a user with basic info like `email`, `username` and `password`.
- Email verification for deliverability from [Hunter](https://hunter.io/)
- Extra user information from [Clearbit/Enrichment](https://clearbit.com/enrichment)
- Authenticate user and acquire token using [JWT](https://jwt.io/).
- Make API calls, with header `Authorization Bearer token`.
- Write post and like/unlike the post.
- Logout user.

## Quick links
- [API Overview](api-overview.md)

## Setup (To run locally)
- Clone this git repository and cd into it:
        
        git clone https://github.com/ahirnish/Tradecore_Assignment.git
        cd Tradecore_Assignment/


- Create a Python 3.6 virtualenv:
        
        virtualenv --python=python3 venv


- activate python virtual environment:
  
        source venv/bin/activate


- Install dependencies:
        
        pip install -r requirements.txt


- Setup Database:
    move to sub-directory `tradecore/`, then run migrations to create database. Using only `sqlite3` DB for development.
    
        cd tradecore/
        python manage.py migrate


- Start server:

        python manage.py runserver


## Quick Setup:
- Using shell script, `setup.sh` placed in project root.

        source setup.sh


## Project's Django Apps:
- : `api` holding all the logics and interacting with DB


## Third party packages:
- [django-rest-framework](https://github.com/encode/django-rest-framework)
- [django-rest-framework-jwt](https://github.com/GetBlimp/django-rest-framework-jwt)
- [requests](https://github.com/requests/requests)
- [pyhunter](https://github.com/VonStruddle/PyHunter)
- [clearbit](https://github.com/clearbit/clearbit-python)

## Usage Directions:
- Setup Project
- Load fixtures (optional, but recommended for testing)
- Start django server
- Run the bot

        python Tradecore_Assignment/tradecore/bot.py data.txt

- Use any rest client with Authorization header, to test APIs. [API Overview](api-overview.md)


## Feedback and Queries:
- mail at: [ahirnish@gmail.com](mailto:ahirnish@gmail.com)
