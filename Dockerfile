FROM i386/debian

WORKDIR /app

RUN apt update && apt install gcc make flex bison nasm git g++ -y

# Interactive mode
CMD bash

# Running tests
# CMD make clean && make test