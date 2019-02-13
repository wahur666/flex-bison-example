FROM i386/debian

WORKDIR /opt/cpp/app

RUN apt update && apt install gcc make flex bison nasm git g++ -y

CMD make clean && make test