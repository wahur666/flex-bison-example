# Flex & Bison example
A compiler and interpreter of a toy language. Using *C++*, *Flex* and *Bison*.

## The toy language
The language is called the *While language*. Its different variants often serve educational purposes. It has two types (*boolean* and *natural*), expressions of these two types, assignment instruction, reading from standard input, writing to standard output, branching and looping.

See the *test/\*.ok* files to learn the syntax and semantics of the language.

## Building the project
Make sure you have *g++*, *flex*, *bison* and *nasm* installed. The project was tested with the following versions: g++ 6.3.0, flex 2.6.1, bison 3.0.4, nasm 2.12.01. It might work with other versions as well.

Use the following command to build the project:
```
make
```
Use the following command to run tests:
```
make test
```
Use the following command to cleanup all generated files:
```
make clean
```

## Using the interpreter
The following command executes a While program immediately:
```
./while -i path/to/your/while.program
```

## Using the compiler
The following command compiles a While language program to NASM assembly:
```
./while -c path/to/your/while.program > output.asm
```
To further compile the assembly program to an executable:
```
nasm -felf output.asm
gcc output.o io.c -o output
```
Note: Under 64 bit operating systems, pass the `-m32` option to gcc.
To run the executable output:
```
./output
```

## Docker environment

If you don't want to compile with your local environment, there is a Docker option. Use the following commands in the project root to build and run the Docker image:

```
docker-compose build
docker-compose run compiler-env
```

This will open a bash terminal on the image. All the source files is in the working directory and it can be modify on the host operating system too. The working directory is shared between the host and the container.

To exit the interactive terminal use:
```
exit
```
To stop and remove the environment run:
```
docker-compose down
```

## Known Issues

If you clone the repository on Windows, the line endings will be converted to Windows format, therefore the compiler not run. Expected error message:

```
'.mpilerEnv     | Line 1: Unexpected character: '
CompilerEnv     | Makefile:51: recipe for target 'exec_write_natural' failed
CompilerEnv     | make: *** [exec_write_natural] Error 1
```

### Solution

Download the repository as a Zip file and unpack it. This keeps the file endings as is, not changing to Windows format.

## License
This software is licensed under the MIT license. See the *LICENSE* file for details.
