from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash 

class Post:
    database = "proyecto_schema" #Me gusto mucho colocar el nombre de la database ahi (°u°)
    def __init__(self,data): 
        self.id = data['id']
        self.titulo = data['titulo']
        self.descripcion = data['descripcion']
        self.created_at = data['created_at']
        self.login_id = None #información de inicio de sesión por publicación para la join table
        self.likes_contador = 0 # cantidad de likes por publicación, aparece en la tabla likes en el join
        self.liked_por_Userlogin = False # si al usuario registrado le ha gustado la publicación o no
        
    
    @classmethod 
    def allPost_userslogin(cls): #metodo para recoger tosod los datos de los posts con los users
        query = "SELECT posts.*, logins.username, logins.first_name, logins.last_name FROM posts JOIN logins on login_id = logins.id;"
        resultado = connectToMySQL(cls.database).query_db(query)
        posts = [] 
        for post in resultado: #Buca a traves de 'resultado'
            login_data = { #estos son los datos del login para el dictionary de la login data 
                'login_id' : post['login_id'],
                'username' : post['username'],
                'first_name' : post['first_name'],
                'last_name' : post['last_name']
            }
            post_data={ # los datos del dictionario para la post data 
                'id' : post['id'],
                'titulo' : post['titulo'],
                'descripcion' : post['descripcion'],
                'created_at' : post['created_at'],
                'login_id' : login_data # Esto conecta la login data dentro de la post data
            }
            posts.append((post_data))
        # print(posts)
        return posts 
    

    @classmethod 
    def allPosts_userlogin_likecontador(cls,data):# junta todos los post, informacion del usuario y contador de likes en orden desde el mas reciente (orderby desc)
        query = """SELECT posts.*, logins.username, logins.first_name, logins.last_name, likes_contador.* , posts_likeados_por_usuario.* FROM posts 
        JOIN logins on login_id = logins.id 
        LEFT JOIN (SELECT post_id, COUNT(post_id) as like_contador FROM likes GROUP BY post_id) likes_contador on posts.id = likes_contador.post_id 
        LEFT JOIN (SELECT post_id as like_por_Userlogin FROM likes WHERE login_id = %(id)s) posts_likeados_por_usuario on posts.id = posts_likeados_por_usuario.like_por_Userlogin
        ORDER BY posts.created_at DESC;""" 
        
        resultado = connectToMySQL(cls.database).query_db(query,data) 
        
        posts = [] # 
        for post in resultado: #Buca a traves de 'resultado'
            this_post_instance = cls(post) # creando una instancia de post 
            like_data = { #creating a data dictionary that hold cheer table data
                'post_id': post['post_id'],
                'like_contador': post['like_contador'],
                'like_por_Userlogin': post['like_por_Userlogin']
            }
            login_data = { #data dictionary for login data 
                'login_id' : post['login_id'],
                'username' : post['username'],
                'first_name' : post['first_name'],
                'last_name' : post['last_name']
            }
            post_data={ # data dictionary for post data 
                'id' : post['id'],
                'titulo' : post['titulo'],
                'descripcion' : post['descripcion'],
                'created_at' : post['created_at'],
                'login_id' : login_data
                
            }
            # push login data into class object
            this_post_instance.login_id = login_data
            # push cheer count into class object 
            if post['like_contador'] != None:
                this_post_instance.likes_contador = post['like_contador']
            # determine whether login cheered post or not (id if True, None if False)
            if post['like_por_Userlogin'] != None:
                this_post_instance.liked_por_Userlogin = True
            posts.append((this_post_instance))
        # print("this is Posts Array:", posts)
        # print("this is resultado",resultado)
        return posts 


    @classmethod # this method is not being used 
    def verPosts_Userlogin(cls,data): #specific post with user information 
        query = "SELECT posts.*, logins.username, logins.first_name, logins.last_name FROM posts JOIN logins on logins.id = login_id where posts.id = %(id)s; "
        resultado = connectToMySQL(cls.database).query_db(query,data)
        return resultado[0]

    @classmethod
    def verPost_Userlogin_likes(cls,data): # specific post with user information and cheer information
        query = """SELECT posts.*, logins.username, logins.first_name, logins.last_name, likes_contador.*, posts_likeados_por_usuarios.* FROM posts
        JOIN logins on logins.id = login_id 
        LEFT JOIN (SELECT post_id, COUNT(post_id) as like_contador FROM likes GROUP BY post_id) likes_contador on posts.id = likes_contador.post_id 
        LEFT JOIN (SELECT post_id as like_por_Userlogin FROM likes WHERE login_id = %(id)s) posts_likeados_por_usuarios on posts.id = posts_likeados_por_usuarios.like_por_Userlogin
        where posts.id = %(post_id)s;"""
        resultado = connectToMySQL(cls.database).query_db(query,data) # make the database resultado into a variable "resultado"
        this_post_instance = cls(resultado[0]) # creating an instance of the post 
        # print(resultado)
        # print(resultado[0])
        # print(resultado[0]['like_contador'])
        like_data = { # data dictionary to hold cheer table data 
                'post_id': resultado[0]['post_id'],
                'like_contador': resultado[0]['like_contador'],
                'like_por_Userlogin': resultado[0]['like_por_Userlogin']
            }
        login_data = { #data dictionary to hold login information
                'login_id' : resultado[0]['login_id'],
                'username' : resultado[0]['username'],
                'first_name' : resultado[0]['first_name'],
                'last_name' : resultado[0]['last_name']
            }
        if like_data['like_contador'] != None: #if the number if cheers is over 0 
            this_post_instance.likes_contador = like_data['like_contador'] #make this class instance cheer counts = the ammount
        # determine whether login cheered post or not (id if True, None if False)
        if like_data['like_por_Userlogin'] != None:
            this_post_instance.liked_por_Userlogin = True
        # print(this_post_instance.likes_contador)
        this_post_instance.login_id = login_data # place login data in the instance login_id space 
        return this_post_instance

    @classmethod
    def crear_post(cls,data): # creating a post with insert
        query = "INSERT INTO posts (titulo,descripcion,login_id) VALUES (%(titulo)s, %(descripcion)s, %(login_id)s);"
        return connectToMySQL(cls.database).query_db(query,data)
    
    @classmethod
    def Tus_Posts(cls,data): # viewing posts with login id 
        query = "SELECT * FROM posts WHERE login_id = %(login_id)s ORDER BY posts.created_at DESC;"
        resultado = connectToMySQL(cls.database).query_db(query,data)
        return resultado

    @classmethod
    def Elimina_Post(cls,data): # deleteing posts 
        query = "DELETE FROM posts WHERE id = %(id)s;"
        return connectToMySQL(cls.database).query_db(query,data)
    
    @classmethod
    def likePost(cls,data): # cheering post with the post id and login id 
        query = "INSERT INTO likes (post_id,login_id) VALUES (%(post_id)s,%(login_id)s) ;"
        return connectToMySQL(cls.database).query_db(query,data)
    
    @classmethod
    def unlikePost(cls,data): # unliking post with login id and post id 
        query = "DELETE FROM likes WHERE login_id = %(login_id)s AND post_id = %(post_id)s ;"
        return connectToMySQL(cls.database).query_db(query,data)
    
    @classmethod
    def likeContador(cls,data): #find out how many likes a post has with the count mysql function
        query = 'SELECT COUNT(id) FROM likes where post_id = %(post_id)s ;'
        return connectToMySQL(cls.database).query_db(query,data)