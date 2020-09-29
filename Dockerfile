FROM python:3.7-alpine

RUN apk --no-cache -u add git && apk --no-cache add --virtual build-deps gcc python3-dev musl-dev && \
  git clone https://github.com/gdhgdhgdh/obs-websocket-http.git && cd /obs-websocket-http && pip install -r requrements.txt

CMD /usr/local/bin/python3 /obs-websocket-http/main.py
