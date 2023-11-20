from myapp import db
from myapp import User

from sqlalchemy import text

app = create_app()

# Push the application context
app.app_context().push()
with db.engine.connect() as connection:
    connection.execute(text("ALTER TABLE user ADD COLUMN reset_token VARCHAR(100)"))

db.session.commit()

