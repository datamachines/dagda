FROM golang:1.8-alpine as builder

RUN apk --update add git;
RUN go get -d github.com/optiopay/klar
RUN go build ./src/github.com/optiopay/klar

#FROM alpine:3.8

FROM python:3.6.4-alpine3.6

RUN apk add --no-cache ca-certificates
RUN apk add --no-cache git
COPY --from=builder /go/klar /klar

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip install -r requirements.txt
COPY dagda /opt/app
COPY ./dockerfiles/run.sh /
RUN chmod +x /run.sh
ENTRYPOINT ["/bin/sh","/run.sh"]

