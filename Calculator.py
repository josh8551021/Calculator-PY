"""Calculator.py
"""

NUMS = "1234567890."
OPERATORS = ['(', ')', '^', ['*', '/', chr(247)], ['+', '-']]
INVALID_OPERATOR_COMBINATIONS = ["*+", "++", "---", "-+", "-*", "//", "/*", "*/", "*^", "^*",
                                 "/^", "^/", "+^", "^+", "-^"]


def find_number(chars, decimal_found=False):
    """
    Checks for the end of a number, when a character that is not represented in real numbers is shown
    
    :param chars: list of characters represented in the calculation, in order
    :param decimal_found:
    :return: resultant number
    """
    
    new_num = ""
    for digit_q in chars:
        if decimal_found:
            if digit_q in NUMS and digit_q != '.':
                new_num += digit_q
            else:
                break
        else:
            if digit_q in NUMS:
                new_num += digit_q
                if digit_q == '.':
                    decimal_found = True
            else:
                break
    return new_num


def is_operator(atom, include_parens=False):
    """
    This function takes in a piece of data and outputs whether the piece of data is an operator
    or not based on whether parentheses are included or not.
    
    :param atom: single piece of information in an equation, be it a number or a symbol
    :param include_parens: Whether to include parentheses as an operator. Defaults as false
    :return: whether ATOM is an operator or not
    """
    
    if not include_parens:
        for op in OPERATORS[2:]:
            if str(atom) in op:
                return True
    elif include_parens:
        for op in OPERATORS:
            if str(atom) in op:
                return True
    return False


def balance_parens(expr):
    """
    This function takes in an expression string and balances the parentheses of the expression.
    This is done by adding parentheses to the end or start of the expression wherever necessary.

    :param expr: string expression
    :return: atoms: expression with balanced parentheses
    """
    atoms = expr
    
    start_parens = 0
    end_parens = 0
    for i in range(len(atoms)):
        if atoms[i] == "(":
            end_parens += 1
        elif atoms[i] == ")":
            if end_parens > 0:
                end_parens -= 1
            else:
                start_parens += 1
    
    prepended_parens = '(' * start_parens
    extended_parens = ')' * end_parens
    atoms = prepended_parens + atoms + extended_parens
    
    return atoms


def fetch_carets(expr):
    """
    This function finds all of the '**' in the calculation string and replaces them with '^'
    
    :param expr: string form of an expression
    :return: the expression with all '**' replaced with '^'.
    """
    
    expr = expr.replace("**", '^')
    return expr


def split_calculation(expr):
    """
    Takes the calculation and breaks it into smaller, workable pieces
    
    :param expr: string given calculation
    :return: list sub, contains the pieces of the computation broken up
    """

    sub = []  # creates list for pieces of the expr
    last_int = 0
    
    if expr[0] == '+':
        sub.append('0')
    
    
    # initial compilation of data into calculation
    curr_idx = 0
    while curr_idx < len(expr):
        char = expr[curr_idx]
        if is_operator(char, include_parens=True):
            sub.append(char)
            if char == '(':
                
                # handles positive numbers after parentheses
                if expr[curr_idx+1] == '+':
                    sub.append(0.0)
        
        # computes numbers
        if char in NUMS:
            num = find_number(expr[curr_idx:])
            sub.append(float(num))
            curr_idx += len(num)-1
            
        curr_idx += 1

    index = 0
    # parenthesis rules
    while index < len(sub)-1:
        if sub[index] == ")": 
            if sub[index+1] == "(":
                sub.insert(index+1, "*")
            elif isinstance(sub[index+1], float):
                sub.insert(index+1, "*")

        elif isinstance(sub[index], float):
            if sub[index+1] == "(":
                sub.insert(index+1, "*")


        # handles case where '-' is negative, not minus sign
        elif sub[index] == '-':
            if not isinstance(sub[index-1], float) or index == 0:
                # if read from bottom up, insert order is seen
                sub.insert(index+2, ")")
                sub.insert(index+1, "*")
                sub.insert(index+1, ")")
                sub.insert(index+1, 1.0)
                # minus goes here "-"
                sub.insert(index, 0.0)
                sub.insert(index, "(")
                sub.insert(index, "(")

        index += 1
    return sub


def match_parens(atoms):
    """
    This function takes an expression with properly balanced parentheses as input and returns a dictionary
    with the indices of the parenthesis pairs.
    
    :param atoms: a list of atoms (numbers and symbols)
    :return: a dictionary where key-value pairs represent open parentheses and their corresponding closing parentheses
    """
    
    paren_locs = {}
    paren_stack = []
    for i in range(len(atoms)):
        if atoms[i] == '(':
            paren_stack.append(i)
        elif atoms[i] == ')':
            open_paren = paren_stack.pop()
            paren_locs[open_paren] = i
    
    return paren_locs

def perform_operations(atoms):
    """
    This function is the final phase of calculating an expression. It takes a list of atoms with no parentheses and
    uses basic order of operations to compute a final result.

    :param atoms: a list of atoms that represents calculation.
    :return: the end result of computing the expression given by the list of atoms
    """
    
    for op in OPERATORS[2:]:
        index = 0
        while index < len(atoms):
            item = atoms[index]
            if str(item) in op:
                a = atoms[index - 1]
                b = atoms[index + 1]
                if item == '^':
                    atoms[index] = a ** b
                elif item == '*':
                    atoms[index] = a * b
                elif item == '/' or item == chr(247):
                    atoms[index] = a / b
                elif item == '+':
                    atoms[index] = a + b
                elif item == '-':
                    atoms[index] = a - b
                del atoms[index + 1]
                del atoms[index - 1]
                index -= 1  # index -= 1:  accounts for number in front of symbol
            
            index += 1
    return sum(atoms)


def solve_expr(atoms, paren_pairs=None):
    """
    This function takes in an expression with properly balanced parentheses and computes its solution.

    :param atoms: list of atoms
    :param paren_pairs: a dictionary in which each key-value pair represents an open parenthesis and
        its corresponding closing parenthesis from an expression
    :return: simplified list of atoms
    """
    
    # one-parameter case
    if paren_pairs is None:
        return solve_expr(atoms, match_parens(atoms))
    
    # recursion to eliminate parentheses
    while paren_pairs != {}:        
        first_open = atoms.index('(')
        first_outer_close = paren_pairs.pop(first_open)
        
        sub_expr = atoms[first_open + 1: first_outer_close]
        sub_parens = match_parens(sub_expr)
        
        simp_expr = solve_expr(sub_expr, sub_parens)
        
        atoms = atoms[:first_open] + [simp_expr] + atoms[first_outer_close + 1:]
        paren_pairs = match_parens(atoms)
    
    return perform_operations(atoms)


def all_valid_operators(calculation_string):
    """
    This function tests the initial calculation string for common invalid operators.
    
    :param calculation_string: initial calculation string
    :return: whether all operators are valid or not
    """
    
    for comb in INVALID_OPERATOR_COMBINATIONS:
        if comb in calculation_string:
            return False
    return True


def is_valid(atoms):
    """
    This function tests the validity of an expression that is split into a list of atoms.
    
    :param atoms: list of atoms
    :return: a boolean, whether the expression is sound or not
    """
    
    if is_operator(atoms[-1]):
        return False
    
    for idx in range(len(atoms)-1):
        if type(atoms[idx]) == float:
            if type(atoms[idx+1]) == float:
                return False
        
    return True

def run_calculator():
    """
    This function runs the logic for the calculator not based on mathematics
    
    :return: void function
    """
    
    while True:
        calculation = input(">> ") # enter (34*33-2*(4))/6
        if calculation.lower() == "c":
            break
        
        calculation = balance_parens(calculation)
        calculation = fetch_carets(calculation)
        if not all_valid_operators(calculation):
            print("Enter a valid calculation.")
            continue
            
        atoms = split_calculation(calculation)
        if not is_valid(atoms):
            print("Enter a valid calculation.")
            continue
        
        solution = solve_expr(atoms)
        
        print(solution)


run_calculator()
