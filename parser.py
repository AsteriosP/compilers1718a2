import plex

class ParseError(Exception):
    pass

class MyParser():
    def __init__(self):
        self.st = {}

    def create_scanner(self, fp):
        # keyword print
        k_print = plex.Str("print")

        # operators
        k_not = plex.Str("not")
        k_and = plex.Str("and")
        k_or = plex.Str("or")
        assignment = plex.Str("=")
        parens = plex.Any("()")
        operators = k_not | k_and | k_or | assignment | parens

        # identifier
        letter = plex.Range("azAZ")
        digit = plex.Range("09")
        identifier = letter + plex.Rep(letter | digit)

        # values "T" or "F"
        t_str = plex.NoCase(plex.Str("true", "t", "1"))
        f_str = plex.NoCase(plex.Str("false", "f", "0"))

        # spaces
        space = plex.Rep1(plex.Any(" \n\t"))

        # the dictionary
        lexicon = plex.Lexicon([
            (k_print, plex.TEXT),
            (operators, plex.TEXT),
            (t_str, "TRUE_TOKEN"),
            (f_str, "FALSE_TOKEN"),
            (identifier, "ID"),
            (space, plex.IGNORE)
        ])

        self.scanner = plex.Scanner(lexicon, fp)
        self.look_ahead, self.value = self.next_token()

    def parse(self, fp):
        self.create_scanner(fp)
        fp.seek(0)
        self.text = fp.readlines()
        self.text = [line.strip() for line in self.text]
        self.stmt_list()

    def next_token(self):
        return self.scanner.read()

    def stmt_list(self):
        first_set = ["ID", "print"]
        if self.look_ahead in first_set:
            self.stmt()
            self.stmt_list()
        elif self.look_ahead is None:
            return
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n unknown command at line {} : \n {}".format(self.pos[1] - 1, s))

    def stmt(self):
        if self.look_ahead == "ID":
            self.match("ID")
            self.match("=")
            self.expr()
        elif self.look_ahead == "print":
            self.match("print")
            self.expr()
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n unknown command at line {} : \n {}".format(self.pos[1] - 1, s))

    def expr(self):
        first_set = ["not", "(", "ID", "FALSE_TOKEN", "TRUE_TOKEN"]
        if self.look_ahead in first_set:
            self.term()
            self.term_tail()
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n one of: not, (, ID, bool_value is needed at line {} : \n {}".format(str(self.pos[1] - 1), s))


    def term_tail(self):
        follow_set = [")", "ID", "print"]
        if self.look_ahead == "or":
            self.orop()
            self.term()
            self.term_tail()
        elif self.look_ahead in follow_set or self.look_ahead is None:
            return
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n missing operator at line {} : \n {}".format(self.pos[1] - 1, s))

    def term(self):
        first_set = ["not", "(", "ID", "FALSE_TOKEN", "TRUE_TOKEN"]
        if self.look_ahead in first_set:
            self.notop()
            self.factor()
            self.factor_tail()
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n wait one of: not, (, id, bool_value at line {} : \n {}".format(self.pos[1] - 1, s))

    def factor_tail(self):
        follow_set = [")", "or", "ID", "print"]
        if self.look_ahead == "and":
            self.andop()
            self.notop()
            self.factor()
            self.factor_tail()
        elif self.look_ahead in follow_set or self.look_ahead is None:
            return
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n missing operator at line {} : \n {}".format(self.pos[1] - 1, s))

    def factor(self):
        if self.look_ahead == "(":
            self.match("(")
            self.expr()
            self.match(")")
        elif self.look_ahead == "ID":
            self.match("ID")
        elif self.look_ahead == "FALSE_TOKEN":
            self.match("FALSE_TOKEN")
        elif self.look_ahead == "TRUE_TOKEN":
            self.match("TRUE_TOKEN")
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("A ParsingError occurred at line {} : \n {}".format(self.pos[1] - 1, s))

    def orop(self):
        if self.look_ahead == "or":
            self.match("or")
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n missing operator at line {} : \n {}".format(self.pos[1] - 1, s))

    def andop(self):
        if self.look_ahead == "and":
            self.match("and")
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n missing operator at line {} : \n {}".format(self.pos[1] - 1, s))

    def notop(self):
        if self.look_ahead == "not":
            self.match("not")
        else:
            return

    def match(self, token):
        if self.look_ahead == token:
            self.pos = self.scanner.position()
            self.look_ahead, self.value = self.next_token()
        else:
            spaces = ' ' * (self.pos[2] + 1)
            s = self.text[self.pos[1] - 1] + "\n" + spaces + "^"
            raise ParseError("ParseError: \n missing {} at line {} : \n {}".format(token, self.pos[1] - 1, s))

p = MyParser()
fp = open("test.txt", "r")
try:
    p.parse(fp)
except ParseError as perr:
    print(str(perr))
fp.close()







