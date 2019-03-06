#include "implementation.hh"
#include <iostream>

// Local Helper Declarations

void print_commands(int indent_level, std::list<instruction*>* commands);
void indent(int indent_level);

// Pretty Print for Expressions

void number_expression::print() const {
    std::cout << value;
}

void boolean_expression::print() const {
    std::cout << (value ? "true" : "false");
}

void id_expression::print() const {
    std::cout << name;
}

void binop_expression::print() const {
    std::cout << "(";
    left->print();

    std::cout << ") ";
    std::cout << op;
    std::cout << " (";

    right->print();
    std::cout << ")";
}

void not_expression::print() const {
    std::cout << op;
    std::cout << " (";
    operand->print();
    std::cout << ")";
}

void ternary_expression::print() const {
    std::cout << "(";
    condition->print();
    std::cout << " ? ";
    true_expression->print();
    std::cout << " : ";
    false_expression->print();
    std::cout << ")";
}

// Pretty Print for Instructions

void assign_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << left << " := ";
    right->print();
    std::cout << std::endl;
}

void read_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << "read(" << id << ")" << std::endl;
}

void write_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << "write(";
    exp->print();
    std::cout << ")" << std::endl;
}

void if_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << "if ";
    condition->print();
    std::cout << " then" << std::endl;
    print_commands(indent_level + 1, true_branch);

    if (false_branch != 0) {
        indent(indent_level);
        std::cout << "else" << std::endl;
        print_commands(indent_level + 1, false_branch);
    }

    indent(indent_level);
    std::cout << "endif" << std::endl;
}

void while_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << "while ";
    condition->print();
    std::cout << " do" << std::endl;
    print_commands(indent_level + 1, body);

    indent(indent_level);
    std::cout << "done" << std::endl;
}

void repeat_instruction::print(int indent_level) const {
    indent(indent_level);
    std::cout << "repeat ";
    count->print();
    std::cout << " do" << std::endl;
    print_commands(indent_level + 1, body);

    indent(indent_level);
    std::cout << "done" << std::endl;
}

// Helpers

void print_program(std::string name, std::list<instruction*>* commands) {
    std::cout << "program " << name << std::endl;

    std::map<std::string,symbol>::iterator it;
    for(it = symbol_table.begin(); it != symbol_table.end(); ++it) {
        std::cout << "    "
          << (it->second.symbol_type == 0 ? "boolean" : "natural") << " "
          << it->second.name << std::endl;
    }

    std::cout << "begin" << std::endl;
    print_commands(1, commands);
    std::cout << "end" << std::endl;
}

void print_commands(int indent_level, std::list<instruction*>* commands) {
    std::list<instruction*>::iterator it;
    for(it = commands->begin(); it != commands->end(); ++it) {
        (*it)->print(indent_level);
    }
}

void indent(int indent_level) {
    for (int i = 0; i < indent_level; ++i) {
        std::cout << "    ";
    }
}
