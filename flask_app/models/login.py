from flask_app.models.post import Post  #importando La clase Post porque la necesito jaja 
from flask_app import app # immportando app de __init__.py 
from flask_app.config.mysqlconnection import connectToMySQL #importando la conexion con mysql connectToMySQL (pilas si no me funciona revisar si la contraseña es la misma o si no lo instalé en la terminar 'Install flask pymysql')
from flask import flash #importamos flash de flask para los mensajes emergentes de las validaciones 
import re

from flask_bcrypt import Bcrypt  #importando bcrypt para hacer un hash magico que encripte la contraseña (no olvidar escribir en la terminal install flash-bcrypt)
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') #importando re para los caractenes especiales de email
class Login:
    database = "proyecto_schema" #hago una varible para igualar el nombre de la database en mysql y evitar el error de copiarlo mal xD ! (cls.database)
    def __init__(self,data): #__init__  constructor para la clase login
        self.id = data['id']
        self.username = data['username']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.cumple = data['cumple']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    
    @classmethod 
    def save_userlogin(cls,formulario): #Query para obtener el login del user
        query = "INSERT INTO logins (username,first_name,last_name,email,cumple,password) VALUES (%(username)s, %(first_name)s , %(last_name)s , %(email)s, %(cumple)s , %(password)s) ;"
        return connectToMySQL(cls.database).query_db(query,formulario)

    @staticmethod # Validaciones para el user que hace el registro 
    def valida_registro(formulario):
        es_valido = True
        query = "SELECT * FROM  logins WHERE email = %(email)s ;" # Verifica si el email esta en la base de datos
        resultado = connectToMySQL('proyecto_schema').query_db(query,formulario)
        if len(resultado)>= 1: 
            flash("Alguien mas ya tiene este email", 'registro') 
            es_valido = False
        if len(formulario['username'])< 3:
            flash('El username debe de tener al menos 3 letras', 'registro')
            es_valido = False
        if len(formulario['first_name'])< 3:
            flash('El nombre debe de tener al menos 3 letras', 'registro')
            es_valido = False
        if len(formulario['last_name']) < 3:
            flash('El apellido debe de tener al menos 3 letras', 'registro')
            es_valido = False
        if len(formulario['email']) < 6:
            flash('El email debe de tener al menos 6 letras', 'registro')
            es_valido = False
        if len(formulario['cumple']) <7:
            flash('Tu fecha de cumpleaños completa', 'registro')
            es_valido = False
        if len(formulario['password']) < 6:
            flash(' Tu contraseña debe de tener al menos 6 caracteres', 'registro')
            es_valido = False 
        if formulario['password'] != formulario['confirmar_password']:
            flash('Contraseña no coincide', 'registro')
            es_valido = False
        if not EMAIL_REGEX.match(formulario['email']): #si el correo electrónico no coincide con el correo electrónico existente
            flash('Este email es invalido')
            es_valido = False 
        return es_valido

    @staticmethod 
    def valida_update(formulario): #validacion para la actualizacion de informacion del user
        es_valido = True 
        if len(formulario['username'])< 3:
            flash('El username debe de tener al menos 3 letras', 'update')
            es_valido = False
        if len(formulario['first_name'])< 3:
            flash('El nombre debe de tener al menos 3 letras', 'update')
            es_valido = False
        if len(formulario['last_name']) < 3:
            flash('El apellido debe de tener al menos 3 letras', 'update')
            es_valido = False
        if len(formulario['email']) < 6:
            flash('El email debe de tener al menos 6 letras', 'update')
            es_valido = False
        if len(formulario['cumple']) <7:
            flash('Tu fecha de cumpleaños completa', 'update')
            es_valido = False
        if len(formulario['password']) < 6:
            flash('Tu contraseña debe de tener al menos 6 caracteres', 'update')
            es_valido = False 
        if formulario['password'] != formulario['confirmar_password']:
            flash('Contraseña no coincide', 'update')
            es_valido = False
        if not EMAIL_REGEX.match(formulario['email']): #si el correo electrónico no coincide con el correo electrónico existente
            flash('Este email es invalido')
            es_valido = False 
        return es_valido

    @classmethod
    def update(cls,formulario): #classmethod para actualizar la informacion del login
        query = "UPDATE logins SET username = %(username)s, first_name = %(first_name)s, last_name = %(last_name)s, email = %(email)s , cumple = %(cumple)s , password = %(password)s  WHERE id = %(id)s "
        return connectToMySQL(cls.database).query_db(query,formulario)
    

    @classmethod 
    def get_by_email(cls,formulario): #informacion del login por email
        #formulario = {
        #      email: elena@cd.com
        #      password: 123
        #}
        query = "SELECT * FROM logins WHERE email = %(email)s ;"
        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        if len(resultado) < 1:
            return False
        return cls(resultado[0])

    @classmethod 
    def get_by_id(cls,formulario):# informacion del login por id
        query = "SELECT * FROM logins WHERE id = %(id)s ;"
        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        return cls(resultado[0])


    
    @classmethod
    def allUserlogin_seguidos(cls,formulario): #obtiene la informacion de los usuarios seguidos en funcion de userlogin
        query = "SELECT logins.id as user_id, seguir.username, seguidos.*, posts.* FROM logins JOIN seguidos on logins.id = login_id JOIN posts on seguido_id = posts.login_id JOIN logins as seguir on posts.login_id = seguir.id where logins.id = %(id)s;"
        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        print(resultado)
        return resultado  
    
    @classmethod
    def allUserlogin_seguidos_con_likecontador(cls,formulario): #obtiene toda la informacion de users logeados con la cantidas de likes que tiene cada publicacion y su el user dio like o no
        query = """SELECT logins.id as user_id,  seguidos.login_id, seguidos.seguido_id, posts.*,seguir.username, likes_contador.*,posts_likeados_por_usuario.* FROM logins 
            JOIN seguidos on logins.id = login_id 
            JOIN posts on seguido_id = posts.login_id 
            LEFT JOIN (SELECT post_id, COUNT(post_id) as like_contador FROM likes GROUP BY post_id) likes_contador
            on posts.id = likes_contador.post_id
            LEFT JOIN (SELECT post_id as like_por_Userlogin FROM likes WHERE login_id = %(id)s) posts_likeados_por_usuario
            on posts.id = posts_likeados_por_usuario.like_por_Userlogin
            JOIN logins as seguir on posts.login_id = seguir.id 
            where logins.id = %(id)s ORDER BY posts.created_at DESC;"""

        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        posts = []
        for post in resultado:
            like_data = {
                'post_id': post['post_id'],
                'like_contador': post['like_contador'],
                'like_por_Userlogin': post['like_por_Userlogin']
            }
            login_data = {
                'login_id' : post['login_id'],
                'username' : post['username'],
                'seguido_id': post['seguido_id']
            }
            post_data={
                'id' : post['id'],
                'titulo' : post['titulo'],
                'descripcion' : post['descripcion'],
                'created_at' : post['created_at'],
                'login_id' : login_data
                
            }
            this_post_instance = Post(post_data)
            # push login data into class object
            this_post_instance.login_id = login_data
            # push cheer count into class object 
            if post['like_contador'] != None:
                this_post_instance.likes_contador = post['like_contador']
            # determine whether login cheered post or not (id if True, None if False)
            if post['like_por_Userlogin'] != None:
                this_post_instance.liked_por_Userlogin = True  #class Post self.cheered_by_user
            posts.append((this_post_instance))
            
        print("Aqui esta el resultado",resultado)
        return posts 
    
    @classmethod #este método se utiliza para determinar cuántos usuarios sigue el userlogin
    def userlogin_seguidos(cls,formulario):
        query = """SELECT logins.id as user_id,  seguidos.*, seguir.username FROM logins 
            JOIN seguidos on logins.id = login_id 
            JOIN logins as seguir on seguidos.seguido_id = seguir.id 
            where logins.id = %(id)s;"""
        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        # print(resultado)
        return resultado

    @classmethod #este método se usa para saber cuántos usuarios están siguiendo el userlogin
    def userlogin_seguidores(cls,formulario):
        query= """SELECT logins.id as user_id,  seguidos.*, seguir.username FROM logins 
            JOIN seguidos on logins.id = login_id 
            JOIN logins as seguir on seguidos.login_id = seguir.id 
            where seguido_id = %(id)s;"""
        resultado = connectToMySQL(cls.database).query_db(query,formulario)
        # print(resultado)
        return resultado

    @classmethod
    def seguir_userlogin(cls,formulario): #siguiendo a otro usuario tomando el userlogin id y otro userlogin id como siguiendo_id y colocandolos en la tabla "siguiendo"
        query = "INSERT INTO seguidos (login_id, seguido_id) VALUES (%(login_id)s, %(seguido_id)s) ;"
        return connectToMySQL(cls.database).query_db(query,formulario)

    @classmethod
    def quita_seguir(cls,formulario): #este metodo elimina un seguidor del usuario
        query = "DELETE FROM seguidos WHERE seguido_id = %(seguidos_id)s AND login_id =%(login_id)s; "
        return connectToMySQL(cls.database).query_db(query,formulario)
