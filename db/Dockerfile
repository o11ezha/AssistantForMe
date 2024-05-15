FROM 192.168.192.203:5000/postgres:15

USER root
RUN mkdir -p /oracle/pg_data/archive/ && chmod -R 777 /oracle/pg_data/archive/
COPY init.sql /docker-entrypoint-initdb.d/

USER postgres
CMD ["postgres"]