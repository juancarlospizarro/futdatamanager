# <img src="docs/img/logo.png" alt="Logo" width="60" align="left"> FutDataManager
<br clear="left"/>

**Enlace a la web / Web application URL:** [FutDataManager](https://futdatamanager.alwaysdata.net)<br>
**Documentación técnica / Technical documentation:** [Docs](https://juancarlospizarro.github.io/futdatamanager/)

## 🇪🇸 Descripción
Este proyecto es una aplicación web desarrollada con **Django** que permite la gestión y el análisis estadístico de equipos de fútbol. El objetivo principal es poder ayudar a los entrenadores a tomar mejores decisiones basadas en datos y facilitar la gestión de sus equipos.

### Tecnologías:
* **Backend:** Python 3.13, Django 
* **Frontend:** Django Templates (JavaScript, Bootstrap, JQuery)
* **Base de Datos:** PostgreSQL
* **Contenedores:** Docker & Docker Compose
* **Despliegue:** AlwaysData (Con posibilidad de despliegue en servicios cloud como AWS o Azure mediante Docker)

---

## 🇬🇧 Description
This project is a web application built with **Django** that enables the management and statistical analysis of football teams. The main goal is to help coaches make better data-driven decisions and streamline their team management.

### Tech Stack:
* **Backend:** Python 3.13, Django
* **Frontend:** Django Templates (JavaScript, Bootstrap, JQuery)
* **Database:** PostgreSQL
* **Containerization:** Docker & Docker Compose
* **Deployment:** AlwaysData (Ready for cloud deployment on AWS or Azure via Docker)

---

## Instalación / Installation (Docker)

```bash
# 1. Clonar repositorio / Clone repo
git clone --single-branch --branch docker https://github.com/juancarlospizarro/futdatamanager.git

# 2. Entrar en la carpeta / Navigate to the directory
cd futdatamanager

# 3. Modificar las credenciales del archivo .env.example y crear un nuevo archivo .env con ellas 
# Modify the .env.example credentials and create a new file with them called .env
cp .env.example .env
nano .env

# Si estás en Windows simplemente crea una copia del archivo, lo modificas y lo guardas como .env
# If you are working on Windows just make a copy of the file, modify the copy and save it as .env

# 4. Levantar con Docker / Run with Docker
docker compose up -d