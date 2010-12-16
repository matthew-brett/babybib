""" Parsers for bib files """

DEBUG = True

import re

from docutils.statemachine import StateMachine, State, string2lines

class OutOfBody(State):
    patterns = dict(
        in_entry = r"^@\w+{\w+,")
    initial_transitions = [('in_entry', 'InEntry')]

    def in_entry(self, match, context, next_state):
        return context, next_state, []


class InEntry(State):
    patterns = dict(
        in_field = r"^\s*\w+\s*=\s*{",
        out_of_body = r"^\s*}\s*$")
    initial_transitions = [('in_field', 'InField'),
                           ('out_of_body', 'OutOfBody')]

    def in_field(self, match, context, next_state):
        return context, next_state, []

    def out_of_body(self, match, context, next_state):
        return context, next_state, []


class InField(State):
    patterns = dict(
        in_braces = r".*?{",
        out_of_field = r".*?},?")
    initial_transitions = [('in_braces', 'InBraces'),
                           ('out_of_field', 'InEntry')]

    def in_braces(self, match, context, next_state):
        return context, next_state, []

    def out_of_field(self, match, context, next_state):
        return context, next_state, []


class InBraces(State):
    patterns = dict(
        in_braces = r".*?{",
        out_of_braces = r".*?}")
    initial_transitions = [('in_braces', 'InBraces'),
                           ('out_of_braces', 'InField')]

    def in_braces(self, match, context, next_state):
        return context, next_state, []

    def out_of_braces(self, match, context, next_state):
        return context, next_state, []


class BibSM(StateMachine):
    state_classes = [OutOfBody, InEntry, InField, InBraces]
    initial_state = 'OutOfBody'

    def __init__(self, debug=DEBUG):
        StateMachine.__init__(self,
                              self.state_classes,
                              self.initial_state,
                              debug)


def parse_str(bib_str):
    sm = BibSM()
    return sm.run(string2lines(bib_str))
