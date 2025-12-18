FROM python:alpine

RUN apk --no-cache add bash postgresql-client shadow

ENV MK_CONFIG=/etc/check_mk

COPY check_mk /etc/
COPY init.py .

CMD [ "python", "./init.py" ]
