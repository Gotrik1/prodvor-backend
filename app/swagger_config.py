
from flask import send_from_directory
import os

def add_swagger_route(app):
    @app.route('/openapi.yaml')
    def serve_openapi_spec():
        # Отдаем файл из корневой директории проекта
        return send_from_directory(os.path.join(app.root_path, '..'), 'openapi.yaml', mimetype='text/yaml')
