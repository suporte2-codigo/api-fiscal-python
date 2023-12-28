FROM ubuntu:20.04

ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update

RUN yes "2" | apt install -y \
    build-essential \
    libxml2 \
    openssl \
    libxmlsec1-openssl \
    libxslt-dev \
    libgtk2.0-0 \
    libcanberra-gtk-module \
    xvfb \
    python3-pip

RUN apt install -y \
    wget

WORKDIR /home
RUN wget -O libacbrnfe64.so http://www2.codigosistemas.com.br/acbr/libacbrnfe64.so
RUN mv libacbrnfe64.so /usr/lib/x86_64-linux-gnu

RUN ln -s /usr/lib/x86_64-linux-gnu/libxmlsec1.so.1 /usr/lib/x86_64-linux-gnu/libxmlsec1.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libxmlsec1-openssl.so.1 /usr/lib/x86_64-linux-gnu/libxmlsec1-openssl.so
RUN ln -s /usr/lib/x86_64-linux-gnu/libxml2.so.2 /usr/lib/x86_64-linux-gnu/libxml.so

# COPY requirements.txt requirements.txt

WORKDIR /usr/src/app

COPY . .

RUN pip3 install -r requirements.txt

COPY run.sh /app/run.sh
RUN chmod 0755 /app/run.sh

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
EXPOSE 5000

ENTRYPOINT ["bash", "/app/run.sh"]