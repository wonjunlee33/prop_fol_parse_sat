# prop_fol_parse_sat

## Parser Brief
### For COMP0009: Logic and Database Theory October 20, 2023
#### 1. TECHNICAL BRIEF
In this course, you will be tasked with writing a propositional and first order tableau, using Python. To assist you with this task, we have decided to release the language specification that we will be using for the coursework early, so you can have some time to write the parser before actually implementing the tableau program. We will also be releasing a parser verification program, which we will be creating shortly, where you will be able to submit your parsers, to test that they indeed parse the grammar as intended. Once the verification program is complete, you will be instructed on how to modify your parsing routine to have it be testable with our online testing tool.
IMPORTANT: Your file must not include any import statements.
Below we define both the language of propositional and first order logic. We limit our propositional letters to p,q,r,s, and our binary connectives to con- junctions, disjunctions, and implications. White space or extra brackets are not allowed in formulas.

```
FMLA := PROP   (Proposition)
      | ~FMLA   (Negation)
      | (FMLA*FMLA)   (Binary Connective)
      
PROP := p|q|r|s   * := /\|\/|=>   (and, or, implies)
```
            
Similarly for FOL, we limit our variables to x, y, z, w, no function symbols, and the only predicates are binary predicates P, Q, R, S.

```
var := x|y|z|w
PRED := P|Q|R|S  * := /\|\/|=>
FMLA := PRED(var,var) (Atom)
| ~FMLA  (Negation)
| EvarFMLA  (Existentially Quantified)
| AvarFMLA   (Universally Quantified)
| (FMLA*FMLA)  (Binary Connective)
```

To see some examples, see sample input/output files. The input file should
have the first line containing PARSE in order for the program to produce parser
output, or SAT to produce satisfiability output (or both). The remaining lines
should be propositional or first order formulas.

If a formula is parsed as a formula, you should construct a Tableau and
see if it has an open branch. For propositional formulas, you will be asked to
determine whether or not it is satisfiable. For first order logic formulas, you
may assume there are no free variables. You will be asked to try and determine
satisfiability, however, the tableau might never close. Thus, if you are required
to add more than 10 new constants on all open branches under some reasonable
fair schedule, you may leave satisfiability undetermined.

#### 2. ASSESSMENT CRITERIA
You should submit a single file, tableau.py. It will be tested against five sample
input files - it should be able to run as is on the lab machines using the below
command, provided there is an input.txt file in the same directory.
```
python3 tableau.py > output.txt
```
A test will pass if and only if the output.txt file matches the model output
file. If your program does not finish computing within a minute, it will timeout
and the test will fail. You will be awarded marks according to the table below:

Task Marks:
- Correctly parse propositional formulas: 20
- Correctly determine SAT for propositional formulas: 20
- Correctly parse first order logic formulas: 20
- Correctly determine SAT for FOL sentences that will not result in a loop under any schedule: 20
- Correctly determine SAT for any FOL sentence, up to assigning 10 variables: 20

#### 3. TESTING YOUR SUBMISSION 
Before submitting your code, you will be able to test it via a web app as many times as you’d like. It will show your
output.txt file for the public test cases as well as the mark your submission would
get when tested against the five secret input files.
Note that we monitor these submissions and that we will investigate any
suspicions we may have of cheating by using this app in ways other than it was
intended to be used. Anyone found cheating will receive a mark of 0 and may
be referred to the academic misconduct board.
Make sure to test your submission from the cs network. You may choose to
use the cs vpn services as described in the CSWall section of https://tsg.cs.
ucl.ac.uk/working-from-home/. Once connected, you will be able to use the
app at http://logic2023.cs.ucl.ac.uk/.
