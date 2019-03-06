#include "implementation.hh"

// Symbol Table

std::map<std::string, symbol> symbol_table;

// Local Helper Declarations

type operand_type(std::string op);
type return_type(std::string op);

// Type Checks for Expressions

void symbol::declare() {
    if(symbol_table.count(name) > 0) {
        error(line, std::string("Re-declared variable: ") + name);
    }
    symbol_table[name] = *this;
}

type number_expression::get_type() const {
    return natural;
}

type boolean_expression::get_type() const {
    return boolean;
}

type id_expression::get_type() const {
    if(symbol_table.count(name) == 0) {
        error(line, std::string("Undefined variable: ") + name);
    }
    return symbol_table[name].symbol_type;
}

type binop_expression::get_type() const {
    if(op == "=") {
        if(left->get_type() != right->get_type()) {
            error(line, "Left and right operands of '=' have different types.");
        }
    } else {
        if(left->get_type() != operand_type(op)) {
            error(line, std::string("Left operand of '") + op + "' has unexpected type.");
        }
        if(right->get_type() != operand_type(op)) {
            error(line, std::string("Right operand of '") + op + "' has unexpected type.");
        }
    }
    return return_type(op);
}

type not_expression::get_type() const {
    if(operand->get_type() != boolean) {
        error(line, "Operand of 'not' is not boolean.");
    }
    return boolean;
}

type ternary_expression::get_type() const {
    if (condition->get_type() != boolean) {
        error(line, "Condition of '?:' expression is not boolean.");
    }

    if (true_expression->get_type() != false_expression->get_type()) {
        error(line, "The sides of '?:' expression are not of the same type.");
    }

    return true_expression->get_type();
}

// Type Checks for Instructions

void assign_instruction::type_check() {
    if(symbol_table.count(left) == 0) {
        error(line, std::string("Undefined variable: ") + left);
    }
    if(symbol_table[left].symbol_type != right->get_type()) {
        error(line, "Left and right hand sides of assignment are of different types.");
    }
}

void read_instruction::type_check() {
    if(symbol_table.count(id) == 0) {
        error(line, std::string("Undefined variable: ") + id);
    }
}

void write_instruction::type_check() {
    exp_type = exp->get_type();
}

void if_instruction::type_check() {
    if(condition->get_type() != boolean) {
        error(line, "Condition of 'if' instruction is not boolean.");
    }
    type_check_commands(true_branch);
    type_check_commands(false_branch);
}

void while_instruction::type_check() {
    if(condition->get_type() != boolean) {
        error(line, "Condition of 'while' instruction is not boolean.");
    }
    type_check_commands(body);
}

void repeat_instruction::type_check() {
    if (count->get_type() != natural) {
        error(line, "Count of 'repeat' instruction is not natural.");
    }

    type_check_commands(body);
}

// Helpers

type operand_type(std::string op) {
    if(op == "+" || op == "-" || op == "*" || op == "/" || op == "%" ||
            op == "<" || op == ">" || op == "<=" || op == ">=") {
        return natural;
    } else {
        return boolean;
    }
}

type return_type(std::string op) {
    if(op == "+" || op == "-" || op == "*" || op == "/" || op == "%") {
        return natural;
    } else {
        return boolean;
    }
}

void type_check_commands(std::list<instruction*>* commands) {
    if(!commands) {
        return;
    }

    std::list<instruction*>::iterator it;
    for(it = commands->begin(); it != commands->end(); ++it) {
        (*it)->type_check();
    }
}
