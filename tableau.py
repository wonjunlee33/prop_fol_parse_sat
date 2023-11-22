
MAX_CONSTANTS = 10

###### parsing formula

def lexer(formula):
    tokens = []
    i = 0
    
    # if formula contains a "/r", change it to "//r" (special case)
    if "\r" in formula:
        formula = formula.replace("\r", "\\r")
        
    # if formula contains a "\\/", "/\\", or "=>", check if there are brackets
    if "\\/" in formula or "/\\" in formula or "=>" in formula:
        if not "(" in formula or not ")" in formula:
            # print("Error: formula must be enclosed in brackets")
            return None
    
    # check if there are equal numbers of "(" and ")"
    if formula.count("(") != formula.count(")"):
        # print("Error: formula must have equal numbers of '(' and ')'")
        return None

    # go through the input formula and tokenize it
    while i < len(formula):
        if formula[i] == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif formula[i] == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        elif formula[i] == ',':
            tokens.append(('COMMA', ','))
            i += 1
        elif formula[i] == '~':
            tokens.append(('NEGATION', '~'))
            i += 1
        elif formula[i:i+2] == '/\\':
            tokens.append(('CONJUNCTION', '/\\'))
            i += 2
        elif formula[i:i+2] == '\\/':
            tokens.append(('DISJUNCTION', '\\/'))
            i += 2
        elif formula[i:i+2] == '=>':
            tokens.append(('IMPLICATION', '=>'))
            i += 2
        elif formula[i] == 'A':
            tokens.append(('FORALL', 'A'))
            i += 1
        elif formula[i] == 'E':
            tokens.append(('EXISTS', 'E'))
            i += 1
        elif formula[i] in 'PQRS':
            tokens.append(('PRED', formula[i]))
            i += 1
        elif formula[i] in 'pqrs':
            tokens.append(('PROP_VAR', formula[i]))
            i += 1
        elif formula[i] in 'xyzwcdefghijkl':
            tokens.append(('FOL_VAR', formula[i]))
            i += 1
        else:
            # Skip whitespaces
            if formula[i] != ' ':
                # print(f"Unknown token: {formula[i]}")
                i += 1
    return tokens

# parser
def parse_formula(tokens):
    if not tokens:
        return None

    token = tokens.pop(0)
    # check if var by itself
    if token[0] == 'PROP_VAR':
        return ('PROP_VAR', token[1])
    elif token[0] == 'FOL_VAR':
        return ('FOL_VAR', token[1])
    # check for negation
    elif token[0] == 'NEGATION':
        subformula = parse_formula(tokens)
        return ('NEGATION', subformula)
    # check for quantifiers
    elif token[0] in ['FORALL', 'EXISTS']:
        var = tokens.pop(0)
        subformula = parse_formula(tokens)
        return (token[0], var[1], subformula)
    # check for predicate expressions
    elif token[0] == 'PRED':
        predicate = token[1]
        # check for beginning of subformula
        if tokens and tokens[0][0] == 'LPAREN':
            tokens.pop(0)
            args = []
            while tokens and tokens[0][0] != 'RPAREN':
                args.append(parse_formula(tokens))
                if tokens and tokens[0][0] == 'COMMA':
                    # handle commas being interpreted weirdly, ie just ignore
                    tokens.pop(0)
            if not tokens or tokens[0][0] != 'RPAREN':
                # print("Expected RPAREN")
                return None
            # check for end of subformula
            tokens.pop(0)
            # exactly two arguments for the predicate
            if len(args) != 2:
                # print("Error: Predicate must have exactly 2 arguments")
                return None
            return ('PRED', predicate, args)
        else:
            # is formula broken?
            # print("Expected LPAREN after PRED")
            return None
    # check for connectives
    elif token[0] == 'LPAREN':
        left = parse_formula(tokens)
        token = tokens.pop(0)
        if token[0] in ['CONJUNCTION', 'DISJUNCTION', 'IMPLICATION']:
            op = token[0]
        else:
            # print(f"Unexpected token after LPAREN: {token}")
            return None
        right = parse_formula(tokens)
        if tokens and tokens[0][0] == 'RPAREN':
            tokens.pop(0)
            return (op, left, right)
        else:
            # print("Expected RPAREN")
            return None
    else:
        # print(f"Unexpected token: {token}")
        return None

# Parse a formula, consult parseOutputs for return values.
def parse(fmla):
    tokens = lexer(fmla)
    parsed = parse_formula(tokens)
    
    if parsed and verify_no_none(parsed):
        if contains_fol_var(parsed) and contains_prop_var(parsed):
            return 0
        if parsed[0] == 'FOL_VAR':
            return 1
        elif parsed[0] == 'NEGATION':
            # return 2 or 7
            # if parsed formula anywhere includes a 'FOL_VAR', return 2
            # else return 7
            if contains_fol_var(parsed):
                return 2
            else:
                return 7
        elif parsed[0] == 'FORALL':
            return 3
        elif parsed[0] == 'EXISTS':
            return 4
        elif parsed[0] in ['CONJUNCTION', 'DISJUNCTION', 'IMPLICATION']:
            # return 5 or 8
            # if parsed formula anywhere includes a 'FOL_VAR', return 5
            # else return 8
            if contains_fol_var(parsed):
                return 5
            else:
                return 8
        elif parsed[0] == 'PROP_VAR':
            return 6
    else:
        # reject
        return 0

# final check to make sure there are no 'None' in the parsed formula
def verify_no_none(parsed_formula):
    if parsed_formula is None:
        return False
    elif isinstance(parsed_formula, tuple):
        # Recursively check subformulas
        for subformula in parsed_formula[1:]:
            if not verify_no_none(subformula):
                return False
        return True
    else:
        # Check for 'None' at the base level
        return True

# helper function to check if a parsed formula contains xyzw
def contains_fol_var(parsed_formula):
    for token in parsed_formula[1:]:
        if isinstance(token, tuple):
            if token[0] == 'FOL_VAR':
                # print("Found FOL_VAR")
                return True
            elif token[0] == 'PRED':
                # print("Assuming it contains FOL_VAR due to PRED")
                return True
            elif contains_fol_var(token):
                return True
    return False

def contains_prop_var(parsed_formula):
    for token in parsed_formula[1:]:
        if isinstance(token, tuple):
            if token[0] == 'PROP_VAR':
                # print("Found FOL_VAR")
                return True
            elif contains_prop_var(token):
                return True
    return False           

# Return the LHS of a binary connective formula
def lhs(fmla):
    formula = lexer(fmla)
    return formula_to_string(parse_formula(formula)[1])

# Return the connective symbol of a binary connective formula
def con(fmla):
    formula = lexer(fmla)
    dict = {'CONJUNCTION': '/\\', 'DISJUNCTION': '\\/', 'IMPLICATION': '=>'}
    return dict[parse_formula(formula)[0]]

# Return the RHS symbol of a binary connective formula
def rhs(fmla):
    formula = lexer(fmla)
    return formula_to_string(parse_formula(formula)[2])

def formula_to_string(parsed_formula):
    if parsed_formula is None:
        return None

    if isinstance(parsed_formula, tuple):
        if parsed_formula[0] == 'NEGATION':
            return f"~{formula_to_string(parsed_formula[1])}"
        elif parsed_formula[0] == 'FORALL':
            return f"A{parsed_formula[1]}{formula_to_string(parsed_formula[2])}"
        elif parsed_formula[0] == 'EXISTS':
            return f"E{parsed_formula[1]}{formula_to_string(parsed_formula[2])}"
        elif parsed_formula[0] == 'IMPLICATION':
            return f"({formula_to_string(parsed_formula[1])}=>{formula_to_string(parsed_formula[2])})"
        elif parsed_formula[0] == 'CONJUNCTION':
            return f"({formula_to_string(parsed_formula[1])}/\\{formula_to_string(parsed_formula[2])})"
        elif parsed_formula[0] == 'DISJUNCTION':
            return f"({formula_to_string(parsed_formula[1])}\\/{formula_to_string(parsed_formula[2])})"
        elif parsed_formula[0] == 'PRED':
            args = ','.join([formula_to_string(arg) for arg in parsed_formula[2]])
            return f"{parsed_formula[1]}({args})"
        else:
            return parsed_formula[1]  # Variables and constants
    else:
        return parsed_formula  # Propositional variables and constants

###### determining satisfiability

# class to represent a tableau
class TableauNode:
    def __init__(self, nodes, closed=False, parent=None):
        self.nodes = nodes
        
def build_tableau(formula):
    root = TableauNode([formula])
    return root

# checks if branch is closed
def is_closed(branch):
    temp_list = []
    for node in branch:
        node = double_negation(node)
        # print(f"node: {node}")
        if node[0] == 'NEGATION':
            if node[1][0] == 'PROP_VAR' or node[1][0] == 'FOL_VAR':
                temp_list.append("-" + node[1][1])
            elif node[1][0] == 'PRED':
                temp_list.append("-" + node[1][1] + node[1][2][0][1] + node[1][2][1][1])
            # print(f"node[0][1][1]: {node[0][1][1]}")
        else:
            if node[0] == 'PROP_VAR' or node[0] == 'FOL_VAR':
                temp_list.append(node[1]) 
            elif node[0] == 'PRED':
                temp_list.append((node[1] + node[2][0][1] + node[2][1][1]))    

    # print(f"temp_list: {temp_list}")
    # Check if any letters in the temp_list have a complement, i.e., p and -p
    for letter in temp_list:
        # print(f"letter: {letter}")
        if letter[0] == '-':
            complement = letter[1:]
            if complement in temp_list:
                return True

    return False

def double_negation(node):
    if node[0] == 'NEGATION' and node[1][0] == 'NEGATION':
        # Remove double negation
        return node[1][1]
    else:
        return node

def alpha_expansion(node):
    # print(f"Alpha expansion for {node}")
    if node[0] == 'CONJUNCTION':
        # Apply alpha expansion for conjunction
        return [node[1], node[2]]
    elif node[0] == 'NEGATION' and node[1][0] == 'DISJUNCTION':
        # Apply alpha expansion for negation of disjunction
        return [('NEGATION', node[1][1]), ('NEGATION', node[1][2])]
    elif node[0] == 'NEGATION' and node[1][0] == 'IMPLICATION':
        # Apply alpha expansion for negation of implication
        return [node[1][1], ('NEGATION', node[1][2])]
    else:
        # print('Not alpha, skipping')
        return node

def beta_expansion(node):
    # print(f"Beta expansion for {node}")
    if node[0] == 'NEGATION' and node[1][0] == 'CONJUNCTION':
        # Apply beta expansion for negation of conjunction
        return [('NEGATION', node[1][1]), ('NEGATION', node[1][2])]
    elif node[0] == 'DISJUNCTION':
        # Apply beta expansion for disjunction
        return [node[1], node[2]]
    elif node[0] == 'IMPLICATION':
        # Apply beta expansion for implication
        return [('NEGATION', node[1]), node[2]]
    else:
        # print('Not beta, skipping')
        return node
     
# changes ~AxA to Ex~A and ~ExA to Ax~A
def clean_fol_formula(formula):
    # change ~ExA to Ax~A
    if formula[0] == 'NEGATION' and formula[1][0] == 'EXISTS':
        formula = ('FORALL', formula[1][1], ('NEGATION', formula[1][2]))
    # change ~AxA to Ex~A
    if formula[0] == 'NEGATION' and formula[1][0] == 'FORALL':
        formula = ('EXISTS', formula[1][1], ('NEGATION', formula[1][2]))
    
    return formula

def delta_expansion(node, var):
    # introducing a new variable
    # variable must be introduced earlier, kept in is_satisfiable
    # change all instances of whatever follows the quantifier to the new variable
    node = clean_fol_formula(node)

    if node[0] == 'EXISTS':
        var_to_change = node[1]
        node = node[2]
        translated_fol_vars = formula_to_string(node)
        
        # 3. change all instances of the variable to the new variable
        translated_fol_vars = translated_fol_vars.replace(var_to_change, var)  
        return parse_formula(lexer(translated_fol_vars))    
    
    # 4. return the node if not
    # print("not delta, skipping")
    return node

def gamma_expansion(node, list_of_existing_vars):
    # using an existing var
    # change all instances of whatever follows the quantifier to the new variables
    node = clean_fol_formula(node)
    if node[0] == 'FORALL':
        var_to_change = node[1]
        node = node[2]
        return_list = []
    
        # 3. change all instances of the variable to the new variable
        for var in list_of_existing_vars:
            translated_fol_vars = formula_to_string(node)
            translated_fol_vars = translated_fol_vars.replace(var_to_change, var)
            return_list.append(parse_formula(lexer(translated_fol_vars)))
            
        # 4. return the new node
        return return_list
    
    # print("not gamma, skipping")
    return node

def is_satisfiable(tableau):
    # way this is structured: 
    # used vars is empty at first, then as we go through the tableau, we add used vars to it
    # available vars is a list of vars that are not used yet, so abcdefghij
    used_vars = []
    available_vars = []
    # fill available_vars with all letters
    for letter in 'cdefghijkl':
        available_vars.append(letter)

    stck = [[tableau.nodes]]
    gamma_nodes = []
    gamma_expanded_formulae = []
    # root
    # print(f"Stck at Root: {stck}")
    num_branches_at_end = 0
    closed_branches = 0
    literals_to_handle = []
    # start looping through all 
    while stck:
        # print(f"USED_VARS", used_vars)
        current_branch = stck.pop(0)
        # print(f"Stck: {stck}")
        # print(f"Current Branch: {current_branch}")
        # check if current_branch is closed
        if is_closed(current_branch):
            # print("Branch is closed")
            closed_branches += 1
            continue
        else:
            # list of branches = list of lists of nodes
            new_branches = []
            # run expansion
            for node in current_branch:
                # print(len(available_vars))
                if len(available_vars) == 0:
                    return 2
                node = clean_fol_formula(node)
                # print(f"gamma_nodes", gamma_nodes)
                # print(f"gamma_expanded_formulae", gamma_expanded_formulae)
                # print(f"dealing with node: {node}")
                # print(f"new_branches: {new_branches}")
                # print(f"gamma_expanded_formulae: {gamma_expanded_formulae}")
                # run through all expansions
                node = double_negation(node)
                alpha_expanded = alpha_expansion(node)
                beta_expanded = beta_expansion(node)
                delta_expanded = delta_expansion(node, available_vars[0])
                gamma_expanded = gamma_expansion(node, used_vars)
                
                # try alpha expansion first
                if alpha_expanded != node:
                    # print(f"new_branches: {new_branches}")
                    # if alpha expansion was successful, add new nodes to new_branches
                    # print(f"alpha_expanded: {alpha_expanded}")
                    if len(new_branches) == 0:
                        new_branches.append(alpha_expanded)
                        # add gamma expansions 
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                    elif len(new_branches) > 0:
                        for branch in new_branches:
                            for a in alpha_expanded:
                                branch.append(a)
                        # add gamma expansions 
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                            
                elif beta_expanded != node:
                    # print(f"new_branches: {new_branches}")
                    # if alpha expansion was not successful, try beta expansion
                    beta_expanded = beta_expansion(node)
                    # print(f"beta_expanded: {beta_expanded}")
                    if len(new_branches) == 0:
                        num_branches_at_end += 1
                        # print("new_branches is empty")
                        for b in beta_expanded:
                            new_branches.append([b])
                        # add gamma expansions    
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                    elif len(new_branches) == 1:
                        num_branches_at_end += 1
                        # print("new_branches has one element")
                        temp = new_branches.pop()
                        for b in beta_expanded:
                            new_branches.append([b])
                        for branches in new_branches:
                            branches.append(temp)
                        # add gamma expansions    
                        if gamma_expanded_formulae:                  
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                    elif len(new_branches) == 2:
                        # print("new_branches has two elements")
                        for branches in new_branches:
                            branches.append(node)
                        # add gamma expansions    
                        if gamma_expanded_formulae:  
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)

                elif delta_expanded != node:
                    # print(f"delta_expanded: {delta_expanded}")
                    # print(f"available_vars: {available_vars}")
                    delta_expanded = delta_expansion(node, available_vars[0])
                    used_vars.append(available_vars[0])
                    # add in gamma expansions for this new variable
                    if gamma_nodes:
                        for g in gamma_nodes:
                            gamma_expanded_formulae.append((gamma_expansion(g, [available_vars[0]]))[0])
                    available_vars.pop(0)
                    
                    if len(new_branches) == 0:
                        # print("new_branches is empty")
                        # print(f"delta_expanded: {delta_expanded}")
                        new_branches.append([delta_expanded])
                        # add gamma expansions    
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    # print(f"branches: {branches}")
                                    branches.append(g)
                    elif len(new_branches) > 0:
                        for branch in new_branches:
                            branch.append(delta_expanded)
                        # add gamma expansions    
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)

                elif gamma_expanded != node:
                    # special case here! if it is gamma_expanded, it must continuously be brought down
                    # and always be expanded 
                    # print(f"gamma_expanded: {gamma_expanded}")
                    gamma_expanded = gamma_expansion(node, used_vars)
                    # add gamma node to gamma_nodes to be added to each branch later as well
                    gamma_nodes.append(node)
                    # also add current gamma_expanded to gamma_expanded_formulae
                    for g in gamma_expanded:
                        gamma_expanded_formulae.append(g)
                    # gamma_expanded is a list of nodes that should be added
                    if len(new_branches) == 0:
                        # print("new_branches is empty")
                        for g in gamma_expanded:
                            new_branches.append([g])
                        # add gamma expansions 
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                    elif len(new_branches) > 0:
                        # print("new_branches has more than 0 elements")
                        for branches in new_branches:
                            for g in gamma_expanded:
                                branches.append(g)
                        # add gamma expansions  
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)

                else:
                    # if alpha and beta were not successful, node must be a literal or predicate, so carry these down
                    # print("literal detected!")
                    if len(new_branches) == 0:
                        literals_to_handle.append(node)
                        # add gamma expansions  
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)
                    elif len(new_branches) > 0:
                        for branch in new_branches:
                            branch.append(node)
                        # add gamma expansions    
                        if gamma_expanded_formulae:
                            for branches in new_branches:
                                for g in gamma_expanded_formulae:
                                    branches.append(g)

            # add literals to all branches  
            for branch in new_branches:
                for literal in literals_to_handle:
                    branch.append(literal)
            
            # nuke gamma_expanded_formulae
            gamma_expanded_formulae = []       
            # nuke literals_to_handle
            literals_to_handle = []
            # add new nodes to current_branch
            # print(f"new_branches AT END: {new_branches}")
            stck += new_branches
        
    # print(f"num_branches_at_end: {num_branches_at_end + 1}")
    # print(f"closed_branches: {closed_branches}")
    if closed_branches == num_branches_at_end + 1:
        return 0
    else:
        return 1

# You may choose to represent a theory as a set or a list
def theory(fmla):
    return TableauNode(parse_formula(lexer(fmla)))
    
# check for satisfiability
def sat(tableau):
    # output 0 if not satisfiable, output 1 if satisfiable, output 2 if the number of constants exceeds MAX_CONSTANTS
    out = is_satisfiable(tableau[0])
    return out

############################################################################################################

#DO NOT MODIFY THE CODE BELOW
f = open('input.txt')

parseOutputs = ['not a formula',
                'an atom',
                'a negation of a first order logic formula',
                'a universally quantified formula',
                'an existentially quantified formula',
                'a binary connective first order formula',
                'a proposition',
                'a negation of a propositional formula',
                'a binary connective propositional formula']

satOutput = ['is not satisfiable', 'is satisfiable', 'may or may not be satisfiable']



firstline = f.readline()

PARSE = False
if 'PARSE' in firstline:
    PARSE = True

SAT = False
if 'SAT' in firstline:
    SAT = True

for line in f:
    if line[-1] == '\n':
        line = line[:-1]
    parsed = parse(line)

    if PARSE:
        output = "%s is %s." % (line, parseOutputs[parsed])
        if parsed in [5,8]:
            output += " Its left hand side is %s, its connective is %s, and its right hand side is %s." % (lhs(line), con(line) ,rhs(line))
        print(output)

    if SAT:
        if parsed:
            tableau = [theory(line)]
            print('%s %s.' % (line, satOutput[sat(tableau)]))
        else:
            print('%s is not a formula.' % line)
            