# Mingle

## Dependencies
- PostgreSQL
- Python 3.X
- Python 3.X Pip
- Pipenv (`pip install pipenv`)

## Setup instructions
```bash
# Create a new virtual environment using Python 3.X
$ pipenv --three

# Install all required packages into the virtual environment
$ pipenv sync
```

> You will need to have PostgreSQL and Auth0 configured, and a database created in PostgreSQL. To follow this, this project uses dotenv, so you will need to have a `.env` file (formatted identical to the [`.env-format`](.env-format) file in this repository) in the root of the project containing (at a minimum):

- Auth0 secret-key
- Auth0 client-id
- Auth0 domain
- Auth0 audience
- Auth0 redirect audience
- Auth0 redirect uri
- Auth0 authorize url
- Auth0 access token url
- PostgreSQL host
- PostgreSQL port
- PostgreSQL database name
- PostgreSQL user
- PostgreSQL password


```bash
# With all of that configured, you can generate the tables using:
$ python3 manage.py --create all
```

# How to run the application
```bash
# Enter the virtual environment
$ pipenv shell

# Run the server
$ python3 run.py
```

## Troubleshooting
Browse and create issues: https://github.com/Durian-Inc/mingle-core/issues

## License
License: Affero GPL v3 License

