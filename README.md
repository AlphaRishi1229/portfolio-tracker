# The trade tracker

The following project exposes the api's by which you can trade and track all your portfolios.

Features:
* Create User
* Create securities
* Update securities
* Create transaction
* Update last transaction
* Delete last transaction
* Show all transactions
* List all securities you own
* Calculate your returns

Tech Stack Used:
* Python - FastAPI
* Postgres - Database
* Docker - Containers

How to use?
* Clone the repo on your local machine.
* To use Docker, you need to install `docker` and `docker-compose` on your system.
* Simply run, `./docker-start.sh start` in the working directory.
* The script will handle everything on its own.
* Once, started open `http://localhost:8000/docs/swagger` in your browser - Here you can see the swagger doc of all the api's
* You can perform everything on the swagger doc itself.

Also, to make database work you will need to upgrade the migrations
* Once you start your server, execute into the container using `docker exec -it portfolio-tracker bash`
* Simply type, `alembic upgrade head` 
* All migrations will be updated.
* To locally check your database you can use the following connection string. 
* `postgresql+psycopg2://smallcase_read_write:smallcaseTracker2021@postgresql/smallcase_tracker`
