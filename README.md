# The `Oboo` API

This repository contains the source code of the `Oboo` web API, used by the `Oboo` Android mobile application.
This project is made up of a single `django` application called `oboo_api`.

This web api exposes various endpoints (listed below) that offer information about buildings, floors and rooms of ISEP buildings:
- `/api/buildings`
- `/api/floors`
- `/api/rooms`
- `/api/timeslots`

This API is not meant to be exposed publicly, but rather to be consumed by the `Oboo` Android mobile application, which allows
students and personnel of ISEP to visualize information about the buildings, floors and rooms of ISEP.

## Development instructions

To start developing on this project, start by cloning this repository.

### Setting up the local development database

To start developing using a local database, perform the following operations:
- [Install MariaDB](https://mariadb.org/download/?t=repo-config)
- Create a new database named `oboo`
- Create a new user with all privileges on the `oboo` database

### Setting up environment variables

Different sensitive and environment-dependent variables are populated using a `.env` file that is not commited to this repository.
In order to start developing on the project, create a `.env` file at the root of this project's directory using the following template:
```properties
# Django
# Set to 0 for production use, 1 for development
DEBUG=0
# Replace this with a securely generated secret key
# See: https://docs.djangoproject.com/en/5.1/ref/settings/#secret-key
SECRET_KEY=<secret-key>
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=<superuser password>
DJANGO_SUPERUSER_EMAIL=<superuser email>
# If using a reverse proxy, add its IP to both fields below
DJANGO_ALLOWED_HOSTS='localhost 127.0.0.1 [::1]'
CSRF_TRUSTED_ORIGINS='http://localhost:8888 http://127.0.0.1:8888'
# Oboo API
# Define the exposed port of the API to suit your needs
OBOO_API_PORT=8888
# Set this to:
# - true to completely delete the database and load the initial provided data
# - false to preserve existing database data
# If you're deploying the application for the first time, set this to true then false
INITIAL_DEPLOY=true
# Database
DB_ENGINE=django.db.backends.mysql
# Database host and port to connect to when using your own development database
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=oboo
DB_USERNAME=<database user username>
DB_PASSWORD=<password of the database user>
DB_ROOT_PASSWORD=<password of the root database user>
# Hyperplanning
HP_URL=https://planning.isep.fr/etudiant
HP_USERNAME=<Hyperplanning username>
# HP_PASSWORD must be in base64 !
HP_PASSWORD=<Hyperplanning password in base64>
```

## Deployment

As of now, the web API can be deployed as a `Docker Compose` stack. The provided `docker-compose.yml` allows the creation of multiple containers that include everything needed to deploy the `Oboo` web API:
- A `gunicorn` container, which hosts the `oboo_api` django application
- A `mariadb` container, which is the backend database used by the `Oboo` API
- An `NGINX` container, which proxies requests to `gunicorn` as well as serving static content.

If you haven't done it already, [install Docker](https://docs.docker.com/engine/install/). Refer to the linked documentation for the installation instructions specific to your distribution.

The `docker-compose.yml` file does not need to be modified. Please adapt the provided `.env` file template with your own values before starting the `Docker compose` stack.

To create the `Docker Compose` stack, simply run the following command in a terminal:
```shell
sudo docker compose up -d
```

This will create the `oboo-api:1.0` `Docker` image and will pull all other dependencies from `DockerHub`.

By default, the `Oboo` API will be exposed on port `8888` (this can be modified in the `.env` file). To access the `Oboo` web API, simply navigate to `http://localhost:8888/api` and start navigating to the various exposed endpoints.

To completely delete the stack and remove all created containers, run the following command in a terminal:
```shell
sudo docker compose down
```

**NB: In order to preserve the data when redeploying the application later, make sure to set the `INITIAL_DEPLOY` parameter to `false` in the `.env` file !**

### Uninstallation

If you want to undeploy the application as well as deleting all of its data, run the following command:
```shell
sudo docker compose down -v --remove-orphans
```

If you wish to remove the images pulled and created by the `Oboo` API, run the following command in a terminal:
```shell
sudo docker image rm oboo-api:1.0 mariadb:lts nginx:stable
```
