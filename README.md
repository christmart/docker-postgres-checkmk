# docker-postgres-checkmk
Companion container to run mk_postgres.py with access to postgres container

This container can run aside of a postgres container and run the
check_mk_agent and mk_postgres.py plugin with access to the postgres
instance of the postgres container.

The container is enabled with a definition like this in the
docker-compose.yml:

  postgres-checkmk:
    image: postgres-checkmk
    restart: always
    depends_on:
      - db
    volumes:
      - /usr/bin/check_mk_agent:/usr/bin/check_mk_agent
      - /usr/lib/check_mk_agent/plugins/mk_postgres.py:/usr/lib/check_mk_agent/plugins/mk_postgres.py
      - ./runpostgres:/run/postgresql
      - ./pgdata/_data/:/var/lib/postgresql
    environment:
      - POSTGRES_UIDNUMBER=999

./pgdata/_data/ is the path of the data directory of the postgres
instance of the postgres container.
./runpostgres is a new directory which will contain the postgres
socket. The line

      - ./runpostgres:/run/postgresql

has to be included into the volumes: section of the postgres
container.

The environment definition POSTGRES_UIDNUMBER is only needed if the
UID of the postgres user in the postgres container is not 70 as is the
standard with alpine linux.

If you see the error message:

FATAL:  role "postgres" does not exist

you have to create the postgres role in your database with:

CREATE ROLE postgres;
ALTER ROLE postgres with login;
