# Этот файл делает "блюпринты" доступными для импорта как `from app.routes import ...`

from .auth import auth_bp
# from .uploads import uploads_bp # Отключено
from .teams import teams_bp
from .users import users_bp
