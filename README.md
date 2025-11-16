# Modular Flask Setup

## Create Environment File
.env file
```
# Flask Configuration
FLASK_CONFIG=development
FLASK_DEBUG=true

# Secret Key (Generate a secure one for production!)
SECRET_KEY=dev-secret-key-change-in-production

# Database Configuration
DATABASE_URL=sqlite:///dev.db
DEV_DATABASE_URL=sqlite:///dev.db
```
## Initialize Database
Use Flask_migrate to Init, Migrate, Upgrade DB
```
flask --app MainApp.wsgi db init
flask --app MainApp.wsgi db migrate
flask --app MainApp.wsgi db upgrade
```

## Run flask
```
python manage.py runserver localhost:5000
```