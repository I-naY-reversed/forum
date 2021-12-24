from sly import Lexer
from sly import Parser
import re
import os
import math
import requests

class BaseLexer(Lexer):
    tokens = {
        IMPORT, ARRAY, IF, ELSE, WHILE, INP, CFILE, RFILE, WFILE, XFILE, LPAREN,
        RPAREN, NAME, NUMBER, FLOAT, EXEC, STRING, FBLOCK, IFBLOCK, LCBR, RCBR,
        TRUE, FALSE, PRINT, TOSTR, TOINT, EQUALS
    }
    ignore = ' \t'
    literals = {
        '=', '+', '-', '/', '*', '(', ')', ',', ';', '{', '}', '|', '>', '<',
        '%', '.', '~', '^', '&', '!', '[', ']'
    }

    IMPORT = r'^import .+'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    STRING = r'\".*?\"'
    FBLOCK = r'\~.*?\~'
    IFBLOCK = r'\%.*?\%'


    NAME['if'] = IF
    NAME['else'] = ELSE
    NAME['while'] = WHILE
    NAME['print'] = PRINT
    NAME['to_str'] = TOSTR
    NAME['to_int'] = TOINT
    NAME['uinp'] = INP

    NAME['cfile'] = CFILE
    NAME['rfile'] = RFILE
    NAME['wfile'] = WFILE
    NAME['xfile'] = XFILE

    NAME['exec'] = EXEC

    EQUALS = r'=='

    LPAREN = r'\('
    RPAREN = r'\)'

    LCBR = r'\{'
    RCBR = r'\}'

    TRUE = r'TRUE'
    FALSE = r'FALSE'

    @_(r'^\[.*\]$')
    def ARRAY(self, token):
        token.value = (token.value[1:-1]).split(',')
        print(token.value)
        return token

    @_(r'\d+\.\d+')
    def FLOAT(self, token):
        token.value = float(token.value)
        return token

    @_(r'\d+')
    def NUMBER(self, token):
        token.value = int(token.value)
        return token

    @_(r'//.*|#>.*')
    def COMMENT(self, token):
        pass

    @_(r'\n+')
    def NEWLINE(self, token):
        self.lineno = t.value.count('\n')

    def error(self, token):
        print(f"Line {self.lineno} has bad char: '{token.value[0]}'")
        self.index += 1


class BaseParser(Parser):
    tokens = BaseLexer.tokens

    precedence = (('left', '+', '-'), ('left', '*', '/'), ('left', '%', '^'),
                  ('left', '>', '<'), ('left', 'EQUALS', 'IF', 'ELSE',
                                       'WHILE'), ('right', 'UMINUS'))

    def __init__(self):
        self.env = {}

    @_('')
    def statement(*args):
        pass

    @_('var_a')
    def statement(self, p):
        return p.var_a

    @_('INP LPAREN STRING RPAREN ">" NAME')
    def var_a(self, p):
        k = input(p.STRING + ': ')
        return ('var_a', p.NAME, f'"{k}"')

    @_('NAME "=" expr')
    def var_a(self, p):
        return ('var_a', p.NAME, p.expr)

    @_('NAME "=" STRING')
    def var_a(self, p):
        return ('var_a', p.NAME, p.STRING)

    @_('NAME "=" EXEC LPAREN FBLOCK RPAREN')
    def var_a(self, p):
        global env
        loc = dict(env)
        exec(str(p.FBLOCK)[1:-1], globals(), loc)
        return ('var_a', p.NAME, loc['returne'])

    @_("PRINT STRING")
    def statement(self, p):
        return p.STRING

    @_("PRINT NAME")
    def statement(self, p):
        return ('print', p.NAME)

    @_('TOSTR LPAREN NUMBER RPAREN')
    def expr(self, p):
        return f'"{str(p.NUMBER)}"'

    @_('TOSTR LPAREN FLOAT RPAREN')
    def expr(self, p):
        return f'"{str(p.FLOAT)}"'

    @_('TOINT LPAREN STRING RPAREN')
    def expr(self, p):
        return int((p.STRING).strip('\"'))

    @_('TOINT LPAREN NAME RPAREN')
    def expr(self, p):
        return ('toint', p.NAME)

    @_('TOSTR LPAREN NAME RPAREN')
    def expr(self, p):
        return ('tostr', p.NAME)

    @_('IMPORT')
    def statement(self, p):
        return ('import', p.IMPORT)

    @_('CFILE LPAREN STRING RPAREN')
    def statement(self, p):
        return ('cfile', p.STRING)

    @_('RFILE LPAREN STRING RPAREN ">" NAME')
    def statement(self, p):
        return ('rfile', p.STRING, p.NAME)

    @_('XFILE LPAREN STRING RPAREN')
    def statement(self, p):
        return ('xfile', p.STRING)

    @_('WFILE LPAREN STRING "," STRING RPAREN')
    def statement(self, p):
        return ('wfile', p.STRING0, p.STRING1)

    @_('NAME LPAREN STRING RPAREN ">" LCBR FBLOCK RCBR')
    def var_a(self, p):
        return ('var_a', p.NAME, p.FBLOCK, p.STRING)

    @_('NAME LPAREN STRING RPAREN')
    def expr(self, p):
        return ('runfunc', p.NAME, p.STRING)

    @_('NAME LPAREN STRING RPAREN ">" NAME')
    def var_a(self, p):
        return ('getfuncout', p.NAME0, p.STRING, p.NAME1)
    
    @_('NAME ">" ARRAY LPAREN NUMBER RPAREN')
    def var_a(self, p):
        return ('index_arr', p.NAME, p.ARRAY, p.NUMBER)

    @_('NAME LPAREN NAME RPAREN ">" NAME')
    def var_a(self, p):
        return ('getfuncoutname', p.NAME0, p.NAME1, p.NAME2)

    @_('WHILE LPAREN NUMBER RPAREN LCBR FBLOCK RCBR')
    def expr(self, p):
        return ('runwhile', p.NUMBER, p.FBLOCK)

    @_('WHILE LPAREN NAME RPAREN LCBR FBLOCK RCBR')
    def expr(self, p):
        return ('runwhilename', p.NAME, p.FBLOCK)

    @_('expr')
    def statement(self, p):
        return p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "%" expr')
    def expr(self, p):
        return ('mod', p.expr0, p.expr1)

    @_('NAME "!" NAME')
    def expr(self, p):
        return ('modn', p.NAME0, p.NAME1)

    @_('expr "^" expr')
    def expr(self, p):
        return ('pow', p.expr0, p.expr1)

    @_('expr ">" expr')
    def expr(self, p):
        return ('grt', p.expr0, p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return ('lst', p.expr0, p.expr1)

    @_('expr EQUALS expr')
    def expr(self, p):
        return ('eqs', p.expr0, p.expr1)

    @_('STRING EQUALS STRING')
    def expr(self, p):
        return ('eqs', p.STRING0, p.STRING1)
    
    @_('NAME EQUALS NAME')
    def expr(self, p):
        return ('eqsn', p.NAME0, p.NAME1)

    @_('NAME EQUALS STRING')
    def expr(self, p):
        return ('eqsns', p.NAME, p.STRING)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('TRUE')
    def expr(self, p):
        return 1

    @_('FALSE')
    def expr(self, p):
        return 0

    @_('IF LPAREN expr RPAREN LCBR IFBLOCK RCBR ELSE LCBR IFBLOCK RCBR')
    def expr(self, p):
        return rm(
            p.IFBLOCK0[1:-1]) if p.expr[1] == 1 or p.expr[1] == '1' else rm(
                p.IFBLOCK1[1:-1])

    @_('IF LPAREN NAME RPAREN LCBR IFBLOCK RCBR ELSE LCBR IFBLOCK RCBR')
    def expr(self, p):
        return ('ife', p.NAME, p.IFBLOCK0, p.IFBLOCK1)

    @_('IF LPAREN NUMBER RPAREN LCBR IFBLOCK RCBR')
    def expr(self, p):
        print(p.NUMBER)
        if p.NUMBER == '1' or p.NUMBER == 1: return rm(p.IFBLOCK[1:-1])
        else: return

    @_('"|" NAME "|"')
    def expr(self, p):
        return ('if', p.NAME)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return p.expr

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('FLOAT')
    def expr(self, p):
        print(p.FLOAT)
        return ('num', p.FLOAT)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)


class BaseExec:
    def __init__(self, tree, env):
        self.env = env
        res = self.walk_tree(tree)

        if res != None and isinstance(res, int):
            print(res)

        if type(res) == str and res[0] == '"':
            print(res)

    def walk_tree(self, node):

        if isinstance(node, int) or isinstance(node, str):
            return node

        if node is None:
            return None

        n0 = node[0]

        if n0 == 'program':
            if node[1] == None:
                self.walk_tree(node[2])
            else:
                self.walk_tree(node[1])
                self.walk_tree(node[2])

        if n0 == 'num' or n0 == 'str': return node[1]

        if n0 == 'add':
            n1 = self.walk_tree(node[1])
            n2 = self.walk_tree(node[2])
            if isinstance(n1, str):
                return '"' + n1.strip('"') + str(n2).strip('"') + '"'
            return n1 + n2

        if n0 == 'sub':
            return self.walk_tree(node[1]) - self.walk_tree(node[2])

        if n0 == 'mul':
            return self.walk_tree(node[1]) * self.walk_tree(node[2])

        if n0 == 'div':
            return int(self.walk_tree(node[1]) / self.walk_tree(node[2]))

        if n0 == 'pow':
            return int(self.walk_tree(node[1])**self.walk_tree(node[2]))

        if n0 == 'mod':
            return self.walk_tree(node[1]) % self.walk_tree(node[2])

        if n0 == 'modn':
            return self.env[node[1]] % self.env[node[2]]

        if n0 == 'lst':
            return 1 if self.walk_tree(node[1]) < self.walk_tree(
                node[2]) else 0

        if n0 == 'grt':
            return 1 if self.walk_tree(node[1]) > self.walk_tree(
                node[2]) else 0

        if n0 == 'eqs':
            return 1 if self.walk_tree(node[1]) == self.walk_tree(
                node[2]) else 0
        
        if n0 == 'eqsn':
            return 1 if self.env[node[1]] == self.env[node[2]] else 0

        if n0 == 'eqsns':
            return 1 if self.env[node[1]] == self.walk_tree(node[2]) else 0

        if n0 == 'var_a':
            self.env[node[1]] = self.walk_tree(node[2])
            return node[1]
        
        if n0 == 'index_arr':
            self.env[node[1]] = self.walk_tree(node[2])[self.walk_tree(node[3])]
            return node[1]

        if n0 == 'print':
            return f'{str(self.env[node[1]])}'

        if n0 == 'tostr':
            return f'"{str(self.env[node[1]])}"'

        if n0 == 'rfile':
            with open(self.walk_tree(node[1])[1:-1], 'r') as stream:
                z = '{}{}{}'.format('"', stream.read(), '"')
                self.env[node[2]] = z
                return z

        if n0 == 'wfile':
            with open(self.walk_tree(node[1])[1:-1], 'w') as stream:
                stream.write(self.walk_tree(node[2]))

        if n0 == 'cfile':
            with open(self.walk_tree(node[1])[1:-1], 'x') as stream:
                return

        if n0 == 'xfile':
            os.remove(str(self.walk_tree(node[1])[1:-1]))

        global env

        if n0 == 'if':
            return rm(self.walk_tree(node[1])[1:-1])

        if n0 == 'ife':
            n1 = int(self.env[node[1]])
            cmds = []
            if n1 == 1:
                cmds = (self.walk_tree(node[2])[1:-1]).split('&')
            else:
                cmds = (self.walk_tree(node[3])[1:-1]).split('&')
            cmds = [rm(x) for x in cmds if x]

            lex = BaseLexer()
            par = BaseParser()
            for cmd in cmds:
                tree = par.parse(lex.tokenize(cmd))
                BaseExec(tree, env)

        if n0 == 'toint':
            n1 = self.env[node[1]]
            return int((str(n1)).strip('\"'))

        if n0 == 'runwhile':
            n1 = self.walk_tree(node[1])
            n2 = self.walk_tree(node[2])
            cmds = (str(n2).replace("\n", '').replace("~", '')).split('$')
            cmds = [x for x in cmds if x]
            lex = BaseLexer()
            par = BaseParser()
            while n1 == 1 or n1 == '1':
                for cmd in cmds:
                    tree = par.parse(lex.tokenize(cmd))
                    BaseExec(tree, env)

        if n0 == 'runwhilename':
            n1 = self.env[node[1]]
            n2 = self.walk_tree(node[2])
            cmds = (str(n2).replace("\n", '').replace("~", '')).split('$')
            cmds = [x for x in cmds if x]
            lex = BaseLexer()
            par = BaseParser()
            while n1 == 1 or n1 == '1':
                for cmd in cmds:
                    tree = par.parse(lex.tokenize(cmd))
                    BaseExec(tree, env)
                n1 = self.env[node[1]]

        if n0 == 'runfunc':
            lenv = {}
            args = self.walk_tree(node[2])[1:-1]
            n1 = self.env[node[1]]
            cmds = (str(n1).replace("\n", '').replace("~", '')).split('$')
            cmds = [x for x in cmds if x]
            if len(cmds):
                lex = BaseLexer()
                par = BaseParser()
                for x in args.split(','):
                    tree = par.parse(lex.tokenize(x))
                    BaseExec(tree, lenv)
                for cmd in cmds:
                    tree = par.parse(lex.tokenize(cmd))
                    BaseExec(tree, lenv)

        if n0 == 'getfuncout':
            lenv = {}
            n1 = self.env[node[1]]
            args = self.walk_tree(node[2])[1:-1]
            cmds = (str(n1).replace("\n", '').replace("~", '')).split('$')
            cmds = [x for x in cmds if x]
            if len(cmds):
                lex = BaseLexer()
                par = BaseParser()
                for x in args.split(','):
                    tree = par.parse(lex.tokenize(x))
                    BaseExec(tree, lenv)
                for cmd in cmds:
                    tree = par.parse(lex.tokenize(cmd))
                    BaseExec(tree, lenv)
            self.env[node[3]] = lenv['returne']

        if n0 == 'getfuncoutname':
            lenv = {}
            args = self.env[node[2]][1:-1]
            n1 = self.env[node[1]]
            cmds = (str(n1).replace("\n", '').replace("~", '')).split('$')
            cmds = [x for x in cmds if x]
            if len(cmds):
                lex = BaseLexer()
                par = BaseParser()
                for x in args.split(','):
                    tree = par.parse(lex.tokenize(x))
                    BaseExec(tree, lenv)
                for cmd in cmds:
                    tree = par.parse(lex.tokenize(cmd))
                    BaseExec(tree, lenv)
            self.env[node[3]] = lenv['returne']

        if n0 == 'import':
            z = self.walk_tree(node[1])[7:]
            try:
                with open(str(z) + ".yx", 'r') as f:
                    cmds = compile(f.read())
                    if len(cmds):
                        lex = BaseLexer()
                        par = BaseParser()
                        for cmd in cmds:
                            tree = par.parse(lex.tokenize(cmd))
                            BaseExec(tree, env)
            except:
                print("Error whilst tring to import {}.".format(z))
            return z

        if n0 == 'var':
            try:
                return self.env[node[1]]
            except:
                print("Variable does not exist in env.")
                return 0


def rm(text):
    parts = re.split(r"""("[^"]*"|'[^']*')""", text)
    parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
    return ''.join(parts)


def compile(text):
    cmds_uf = text.replace("\n", '')
    #parts = re.split(r"""("[^"]*"|'[^']*')""", cmds_uf)
    #parts[::2] = map(lambda s: "".join(s.split()), parts[::2])
    #c = ''.join(parts)
    c = cmds_uf
    with open("main.yxc", 'w') as f:
        f.write(c)

    return [
        x for x in [
            x for x in c.split(';')
            if not x.startswith("#>") and not x.startswith("//")
        ] if x
    ]


env = {}


def run():
    try:
        cmds = []
        with open('main.yx', 'r') as f:
            cmds = compile(f.read())

        if len(cmds):
            lex = BaseLexer()
            par = BaseParser()
            for cmd in cmds:
                tree = par.parse(lex.tokenize(cmd))
                BaseExec(tree, env)
    except:
        pass


def main():
    global env
    cmd = ''
    lex = BaseLexer()
    par = BaseParser()

    while True:
        try:
            # input('\033[92mYX>\033[0m ')
            cmd = input('\033[92mYX>\033[0m ')
        except EOFError:
            print('EOFError')
        if cmd:
            tree = par.parse(lex.tokenize(cmd))
            BaseExec(tree, env)

if __name__ == '__main__':
    main()