# Healthy Bite – Sistema de pedidos saludables

La idea de este proyecto fue armar una aplicación web que permita que los clientes hagan pedidos de comida saludable y que los nutricionistas gestionen todo desde su propio panel.

La app está hecha con Flask, usa SQLite como base de datos y está organizada con blueprints. Además, se agregó login con Google como integración externa.


# Funcionalidades principales

# Clientes
- Crear cuenta o iniciar sesión (con google o normal).
- Ver planes y platos.
- Hacer pedidos.
- Ver recomendaciones que le deja el nutricionista.
- Acceder a su cuenta.

# Nutricionistas
- Iniciar sesión.
- Panel con acceso a gestión.
- Modificar planes y platos.
- Ver y validar pedidos.
- Consultar información de los clientes.
- Crear recomendaciones para cada cliente.


# Autenticación

El sistema usa sesiones de Flask para diferenciar si el usuario es cliente o nutricionista. Según el rol, se habilitan o no distintas rutas. También se agregó Google Auth, que permite iniciar sesión usando una cuenta de Google (se obtienen nombre y mail, y se maneja la sesión igual que con el login normal).

Las variables de Google y la secret key se cargan desde `.env` para no dejar datos sensibles en el repositorio.


# Estructura del proyecto

La estructura principal es la siguiente:

healthy_bite/
auth/ → rutas de login, logout y Google Auth

clientes/ → rutas y vistas del cliente

nutricionistas/ → rutas y vistas del nutricionista

main/ → rutas generales y página de inicio

templates/ → archivos HTML

static/ → estilos CSS y archivos estáticos

db.py → conexión y creación de la base de datos

init.py → App Factory y registro de blueprints

run.py → archivo principal que levanta la aplicación

Archivos adicionales:
requirements.txt

Procfile 

# Cómo ejecutar el proyecto localmente
-Clonar el repositorio desde GitHub.

- Crear un entorno virtual.
 En Windows, por ejemplo:
 py -m venv .venv

- Activar el entorno virtual.
Windows: .venv\Scripts\activate
Instalar las dependencias:
pip install -r requirements.txt

- Crear un archivo .env en la raíz del proyecto con las variables:
 SECRET_KEY=tu_clave
 GOOGLE_CLIENT_ID=tu_id
 GOOGLE_CLIENT_SECRET=tu_secret
 GOOGLE_REDIRECT_URI=http://localhost:5000/login_google/callback


- Ejecutar la aplicación:
 py run.py


- La aplicación arranca en:
 http://localhost:5000


# Despliegue en Render
El proyecto está preparado para funcionar en Render.
Incluye un Procfile que indica cómo iniciar la app usando Gunicorn.
En Render hay que configurar las variables de entorno igual que en el archivo .env local.
La base de datos SQLite se genera automáticamente si no existe.

# Dependencias principales

- Flask
- gunicorn
- google-auth-oauthlib
- python-dotenv
- requests
- sqlite3


link del render: https://healthy-bite.onrender.com
