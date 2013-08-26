""" Parser for bibtex files """

DEBUG = False

from os.path import dirname, join as pjoin
import sys

from .ply import lex
from .ply import yacc

# We are doing our own error recovery, and so don't allow post error tokens
# without further p_error calls.  This is a module global
yacc.error_count = 1

from .btlex import tokens, make_lexer, reset_lexer


class Macro(object):
    """ Class to encapsulate undefined macro references """
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Macro("%s")' % self.name
    def __eq__(self, other):
        return self.name == other.name
    def __ne__(self, other):
        return self.name != other.name


def make_error(t):
    """ Create error marker token to signal read error to parser """
    tok = lex.LexToken()
    tok.type = 'ERRORMARKER'
    tok.value = 'error marker'
    tok.lineno = t.lineno
    tok.lexpos = t.lexpos
    return tok

tokens += ('ERRORMARKER',)

_MYPATH=dirname(__file__)


class BibTeXEntries(object):
    def __init__(self, entries = None,
                 preamble = None,
                 defined_macros = None,
                 undefined_macros = None):
        if entries is None:
            entries = {}
        if preamble is None:
            preamble = []
        if defined_macros is None:
            defined_macros = {}
        if undefined_macros is None:
            undefined_macros = {}
        self.entries = entries
        self.preamble = preamble
        self.defined_macros = defined_macros
        self.undefined_macros = undefined_macros

    def __eq__(self, other):
        return (self.entries == other.entries and
                self.preamble == other.preamble)


class BibTeXParser(object):
    def __init__(self,
                 lexer=None,
                 tokens=tokens,
                 debug=DEBUG,
                 picklefile=None,
                 **kwargs):
        if lexer is None:
            lexer = make_lexer()
        if not debug and picklefile is None:
            picklefile = pjoin(_MYPATH, 'btparse.pkl')
        self.lexer = lexer
        self._stack = []
        self.tokens = tokens
        self.debug = debug
        self.parser = yacc.yacc(
            debug=DEBUG,
            module=self,
            picklefile=picklefile,
            **kwargs)

    def parse(self, txt, debug=False):
        reset_lexer(self.lexer)
        self._results = BibTeXEntries()
        self._results.entries = self.parser.parse(txt,
                                                  lexer=self.lexer,
                                                  tokenfunc = self.get_token,
                                                  debug=debug)
        return self._results

    def warn(self, msg):
        """ Emit warning `msg` """
        sys.stderr.write(msg + '\n')

    def get_token(self):
        stack = self._stack
        if len(stack):
            return stack.pop()
        return self.lexer.token()

    def p_start(self, p):
        """ definitions : entry
                        | throwout
                        | empty
        """
        p[0] = {}
        if not p[1] is None: # entry is tuple, others return None
            key, value = p[1]
            p[0][key] = value

    def p_empty(self, p):
        "empty :"
        pass

    def p_definitions_throwout(self, p):
        " definitions : definitions throwout "
        p[0] = p[1]

    def p_definitionss_entry(self, p):
        " definitions : definitions entry "
        p[0] = p[1]
        key, value = p[2]
        if key in p[0]:
            self.warn('Duplicate key "%s"; replacing' % key)
        p[0][key] = value

    def p_throwouts(self, p):
        """ throwout : macro
                    | preamble
                    | IMPLICIT_COMMENT
                    | EXPLICIT_COMMENT
        """

    def p_entry(self, p):
        """ entry : AT ENTRY LBRACKET CITEKEY COMMA fieldlist RBRACKET
                | AT ENTRY LBRACKET CITEKEY COMMA fieldlist COMMA RBRACKET
                | AT ENTRY LBRACKET CITEKEY COMMA fieldlisterr
        """
        # entries are (citekey, dict) tuples.  Entry types are in ENTRY, and are not
        # case senstive. They go in the fieldlist dictionary as key 'entry type'.
        # The space in the key makes it an illegal bibtex field name, so it can't
        # clash with bibtex fields.  Citekeys are case sensitive
        p[6]['entry type'] = p[2].lower()
        p[0] = (p[4], p[6])

    def p_entry_error(self, p):
        " throwout : AT error ERRORMARKER "
        # Entry is unrecoverable
        self.warn("Syntax error in entry; discarding")

    def p_macro(self, p):
        "macro : AT MACRO LBRACKET NAME EQUALS expression RBRACKET"
        name = p[4].lower()
        self._results.defined_macros[name] = p[6]

    def p_macro_error(self, p):
        "macro : AT MACRO error ERRORMARKER"
        self.warn("Syntax error in macro; discarding")

    def p_preamble(self, p):
        "preamble : AT PREAMBLE LBRACKET expression RBRACKET"
        self._results.preamble += p[4]

    def p_preamble_error(self, p):
        "preamble : AT PREAMBLE error ERRORMARKER"
        self.warn("Syntax error in preamble; discarding")

    def p_fieldlist_from_def(self, p):
        """ fieldlist : fielddef """
        # fieldef is a tuple
        p[0] = dict((p[1],))

    def p_fieldlisterr_from_def(self, p):
        """ fieldlisterr : error ERRORMARKER """
        self.warn("Error in field definition, discarding")
        p[0] = {}

    def p_fieldlist_from_list_def(self, p):
        """ fieldlist : fieldlist COMMA fielddef
        """
        # fielddef is a tuple, fieldlist is a dictionary
        key, value = p[3]
        p[0] = p[1]
        p[0][key] = value

    def p_fieldlisterr_from_list_error(self, p):
        """ fieldlisterr : fieldlist error ERRORMARKER
        """
        # Signals error to entry
        self.warn("Syntax error in field list; discarding remainder")
        # Try and keep fieldlist up til now
        p[0] = p[1]

    def p_fielddef(self, p):
        """ fielddef : NAME EQUALS expression"""
        p[0] = (p[1].lower(), p[3])

    def p_expr_name(self, p):
        " expression : NAME "
        # reference to a macro
        name = p[1].lower()
        d_macros = self._results.defined_macros
        if name in d_macros:
            p[0] = d_macros[name]
            return
        # Placeholder and reference to undefined macros
        p[0] = [Macro(name)]
        ud_macros = self._results.undefined_macros
        if name not in ud_macros:
            ud_macros[name] = [p[0]]
        else:
            ud_macros[name].append(p[0])

    def p_expr_number(self, p):
        """ expression : NUMBER """
        p[0] = [p[1]]

    def p_expr_string(self, p):
        """ expression : quotedstring
                    | curlystring
        """
        p[0] = p[1]

    def p_string_quoted(self, p):
        " quotedstring : QUOTE stringcontents QUOTE "
        p[0] = p[2]

    def p_string_curlied(self, p):
        " curlystring : LCURLY stringcontents RCURLY "
        p[0] = p[2]

    def p_scont_basic(self, p):
        """ stringcontents : STRING
                        | curlystring
        """
        p[0] = [p[1]]

    def p_scont_empty(self, p):
        " stringcontents : empty "
        p[0] = []

    def p_scont_appending(self, p):
        """ stringcontents : stringcontents STRING
                        | stringcontents curlystring
        """
        p[0] = p[1] + [p[2]]

    def p_expr_hash(self, p):
        """ expression : expression HASH expression """
        p[0] = p[1] + p[3]

    def p_error(self, t):
        self.warn("Syntax error at token %s, value %s, line no %d"
                  % (t.type, t.value, t.lineno))
        # Read ahead to next AT, and put back on the stack
        while 1:
            tok = self.get_token()             # Get the next token
            if not tok or tok.type == 'AT': break
        if tok:
            self._stack.append(tok)
        # Put an error marker on the stack to resynchronize
        self._stack.append(make_error(t))


# Top level convenience object and function
parser = BibTeXParser()
parse = parser.parse
