from dotenv import load_dotenv
load_dotenv() # Загружает переменные окружения из .env файла

import json
import click
import os
from flask.cli import AppGroup
from app import create_app
from flasgger import Swagger

# This creates a new command group 'swagger'
swagger_cli = AppGroup('swagger', help='Commands for Swagger documentation.')

@swagger_cli.command('generate')
def generate_swagger_command():
    """Generates the swagger.json file by querying the spec endpoint."""

    # We need a temporary app that is configured for spec generation
    generator_app = create_app(init_swagger=False)

    template = {
        "swagger": "2.0",
        "info": {
            "title": "Sport Matching API",
            "description": "A RESTful API for a sports team and player matching platform.",
            "version": "1.0.0"
        },
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        }
    }

    # Initialize a temporary Swagger instance for generation.
    Swagger(generator_app, template=template, parse=True)

    # Use a test client on the temp app to get the spec
    try:
        # The default endpoint for the spec in flasgger is /apispec_1.json
        with generator_app.test_client() as client:
            response = client.get('/apispec_1.json')
            
            if response.status_code != 200:
                error_message = response.get_data(as_text=True)
                click.echo(f"Error: Received status code {response.status_code} when trying to get spec. Details: {error_message}")
                return

            spec = response.get_json()

        # Get the path to the static folder and ensure it exists
        static_dir = os.path.abspath(generator_app.static_folder)
        os.makedirs(static_dir, exist_ok=True)
        
        # We will name our file swagger.json for convention
        file_path = os.path.join(static_dir, 'swagger.json')
        with open(file_path, 'w') as f:
            json.dump(spec, f, indent=2)
            
        click.echo(f'Successfully generated swagger.json at {file_path}')

    except Exception as e:
        click.echo(f"An error occurred during swagger generation: {e}")

# This is the main application factory for the Flask CLI
def create_flask_app():
    app = create_app()
    app.cli.add_command(swagger_cli)
    return app

# The flask command expects to find an 'app' variable, which is our factory's result
app = create_flask_app()
