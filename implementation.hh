#ifndef IMPLEMENTATION_HH
#define IMPLEMENTATION_HH

#include <string>
#include <list>
#include <map>

// Common Elements

enum mode {compiler, interpreter};
extern mode current_mode;

enum type {boolean, natural};
struct symbol {
    symbol() {}
    symbol(int _line, std::string _name, type _type);
    void declare();
    std::string get_code();
    int get_size();
    int line;
    std::string name;
    type symbol_type;
    std::string label;
};

extern long id;
extern std::string next_label();

extern std::map<std::string, symbol> symbol_table;
extern std::map<std::string, unsigned> value_table;

// AST Metamodel of Expressions

class expression {
  public:
    virtual type get_type() const = 0;
    virtual ~expression();
    virtual std::string get_code() const = 0;
    virtual unsigned get_value() const = 0;
    virtual void print() const = 0;
};

class number_expression : public expression {
  public:
    number_expression(std::string text);  
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;  
    void print() const;
  private:
    unsigned value;
};

class boolean_expression : public expression {
  public:
    boolean_expression(bool _value);  
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;
    void print() const;
  private:
    bool value;
};

class id_expression : public expression {
  public:
    id_expression(int line, std::string _name);  
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;
    void print() const;
  private:
    int line;
    std::string name;
};

class binop_expression : public expression {
  public:
    binop_expression(int _line, std::string _op, expression* _left, expression* _right);
    ~binop_expression();
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;
    void print() const;
  private:
    int line;
    std::string op;
    expression* left;
    expression* right;
};

class not_expression : public expression {
  public:
    not_expression(int _line, std::string _op, expression* _operand);
    ~not_expression();
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;
    void print() const;
  private:
    int line;
    std::string op;
    expression* operand;
};

class ternary_expression : public expression {
  public:
    ternary_expression(int _line, expression* _condition,
        expression* _true_expression, expression* _false_expression);
    ~ternary_expression();
    type get_type() const;
    std::string get_code() const;
    unsigned get_value() const;
    void print() const;
  private:
    int line;
    expression* condition;
    expression* true_expression;
    expression* false_expression;
};

// AST Metamodel of Instructions

class instruction {
  public:
    instruction(int _line);
    virtual ~instruction();
    virtual void type_check() = 0;
    virtual std::string get_code() = 0;
    virtual void execute() = 0;
    int get_line();
    virtual void print(int indent_level) const = 0;
  protected:
    int line;
};

class assign_instruction : public instruction {
  public:
    assign_instruction(int _line, std::string _left, expression* right);
    ~assign_instruction();
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    std::string left;
    expression* right;
};

class read_instruction : public instruction {
  public:
    read_instruction(int _line, std::string _id);
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    std::string id;
};

class write_instruction : public instruction {
  public:
    write_instruction(int _line, expression* _exp);
    ~write_instruction();
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    expression* exp;
    type exp_type;
};

class if_instruction : public instruction {
  public:
    if_instruction(int _line, expression* _condition, std::list<instruction*>* _true_branch, std::list<instruction*>* _false_branch);
    ~if_instruction();
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    expression* condition;
    std::list<instruction*>* true_branch;
    std::list<instruction*>* false_branch;
};

class while_instruction : public instruction {
  public:
    while_instruction(int _line, expression* _condition, std::list<instruction*>* _body);
    ~while_instruction();
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    expression* condition;
    std::list<instruction*>* body;
};

class repeat_instruction : public instruction {
  public:
    repeat_instruction(int _line, expression* _count, std::list<instruction*>* _body);
    ~repeat_instruction();
    void type_check();
    std::string get_code();
    void execute();
    void print(int indent_level) const;
  private:
    expression* count;
    std::list<instruction*>* body;
};

// Semantic API

void type_check_commands(std::list<instruction*>* commands);
void execute_commands(std::list<instruction*>* commands);
void generate_code(std::list<instruction*>* commands);
void print_program(std::string name, std::list<instruction*>* commands);

// Common Helpers

void error(int line, std::string text);
void delete_commands(std::list<instruction*>* commands);

#endif // IMPLEMENTATION_HH
