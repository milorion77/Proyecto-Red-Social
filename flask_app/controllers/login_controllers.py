
from flask_app.models.post import Post #importo la clase Posts en models 
from flask_app.models.login import Login #importo la clase Login en models
from flask_app import app # importo aplicacion desde  __init__.py 
from flask import redirect, request, session, render_template, flash 
from flask_bcrypt import Bcrypt  #recordar haber instalado por enesima vez esto jaja (install flash-bcrypt)  
bcrypt = Bcrypt(app) 


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login') 
def loginpage():
    return render_template('login.html')

@app.route('/signup') 
def signup():
    return render_template('signup.html')

@app.route('/registro', methods = ['POST']) #Esta es la ruta del registro
def registra_usuario():
    #Validar la información ingresada
    if not Login.valida_registro(request.form): #si retorna falso, redirecciona a signup
        return redirect('/signup')
    password_hash = bcrypt.generate_password_hash(request.form['password']) # con esto encriptamos el password del usuario
    print(password_hash)
    formulario ={ 
        'username': request.form['username'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'cumple': request.form['cumple'],
        'password': password_hash # variable que contiene contraseña hash encriptada en la base de datos
    }
    
    login_id =Login.save_userlogin(formulario) #Recibo el identificador de mi nuevo usuario logueado y lo meto a la base de datos
    session['login_id'] = login_id 
    return redirect('/homepage')

@app.route('/login', methods =['POST']) 
def login():
    formulario = {
        'email': request.form['email'] #Registra el email en el diccionario 'formulario'
    }
    login_formulario = Login.get_by_email(formulario) #Llama la informacion del login por email
    
    #Probando mensaje flash desde controller
    
    if not login_formulario: #Esto pregunta al query MYSQL y si retorna falso sale mensaje flash
        flash('Hay algo mal en tu email o contraseña', 'login')
        return redirect('/login')
    if not bcrypt.check_password_hash(login_formulario.password, request.form['password']):
        flash('Hay algo mal en tu email o contraseña', 'login')
        return redirect('/login')
    session['login_id'] = login_formulario.id 
    return redirect('/homepage')

@app.route('/homepage')
def homepage():
    if 'login_id' not in session: #verifica si user logueado esta en sesion
        return redirect('/logout') # esto lo saca si no lo esta, (que lo saque por chismoso xD)
    formulario={
        'id':session['login_id']
    }
    login = Login.get_by_id(formulario)  #Esto ejecuta lo que toma la informacion del loginid con la session
    seguidos = Login.userlogin_seguidos(formulario) #toma la informacion de cuantos usuarios sigues
    seguidores= Login.userlogin_seguidores(formulario) # toma la informacion de cuantos usuarios te siguen
    posts = Post.allPosts_userlogin_likecontador(formulario) #Esto ejecuta lo que toma todos los post con el user y el contador de likes 
    return render_template('homepage.html' , login = login , posts=posts, num_de_seguidos = len(seguidos), num_de_seguidores = len(seguidores) ) #connecto las variables con el html

@app.route('/profile') #
def perfil():
    if 'login_id' not in session: #verifica si user logueado esta en sesion
        return redirect('/logout')
    formulario={
        'id':session['login_id']
    }
    login = Login.get_by_id(formulario) #Esto toma la informacion del login usando la login id de la sesion
    seguidos = Login.userlogin_seguidos(formulario) #toma la informacion de cuantos usuarios sigues
    seguidores= Login.userlogin_seguidores(formulario) # toma la informacion de cuantos usuarios te siguen
    return render_template('profile.html', login = login, num_de_seguidos = len(seguidos), num_de_seguidores = len(seguidores) ) #Esta informacion esta en profile.html

@app.route('/update', methods =['POST']) 
def update_perfil():
    if 'login_id' not in session: 
        return redirect('/logout')
    if not Login.valida_update(request.form): 
        return redirect('/profile')
    password_hash = bcrypt.generate_password_hash(request.form['password']) 
    formulario ={
        'id': request.form['id'],
        'username': request.form['username'],
        'first_name': request.form['first_name'],
        'last_name': request.form['last_name'],
        'email': request.form['email'],
        'cumple': request.form['cumple'],
        'password': password_hash
    }
    Login.update(formulario) #actualiza la informacion del formulario
    return redirect('/homepage')

@app.route('/following') #ruta para ver las publicaciones que sigue el userlogin
def seguidos():
    if 'login_id' not in session:#verifica si user logueado esta en sesion
        return redirect('/logout')
    formulario={
        'id':session['login_id']
    }
    login = Login.get_by_id(formulario)

    posts = Login.allUserlogin_seguidos_con_likecontador(formulario)#Esto toma la informacion de todos los seguidores con la cantidad de likes que tiene cada publicacion  
    return render_template('following.html', login=login, posts = posts)


@app.route('/logout')
def logout():
    session.clear() # borra sesion y sale de la app
    return redirect('/login')