#EJECUTA nuestra aplicación
from flask_app import app

#Importando mi controlador
from flask_app.controllers import login_controllers,post_controllers

#pipenv install flask pymysql flask-bcrypt
#pipenv shell
#python server.py -> py python

if __name__ == "__main__":
    app.run(debug=True)