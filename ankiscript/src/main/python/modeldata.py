
import collections
from .database import createModel, editModel

Note = collections.namedtuple('Note', ['name', 'cloze', 'css'])
Parameter = collections.namedtuple('Parameter', ['name', 'values'])

class Template:
    def __init__(self, name, deck, front, back):
        self.name = name
        self.deck = deck
        self.front = front
        self.back = back

    def __eq__(self, other):
        return self.name == other.name and self.deck == other.deck and self.front == other.front and self.back == other.back

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Template({0}, {1}, {2}, {3})'.format(self.name, self.deck, self.front, self.back)


# this class should do all param substitution (nothing else should deal with parameters)
class ModelData:

    def __init__(self, course, datasource):
        self._course = course
        self._datasource = datasource

    def __enter__(self):
        self._action = None
        self._note = None
        self._fields = []
        self._templates = []
        self._params = []
        self._translations = {}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._action is not None:
            self._action(self)
        return False

    def set_note(self, action, name, cloze):
        self._action = action

        # populate css
        css = self._datasource.read(['config', 'templates', name], name + '.css')
        self._note = Note(name, False, css)

        # for cloze notes a card is added automatically as they only have 1 card type & no default deck
        # note: must only set note cloze flag to True after adding cloze template
        if cloze:
            self.add_templates(['cloze'], None)
            self._note = Note(name, cloze, css)

    def add_parameter(self, name, values):
        self._params.append(Parameter(name, values))

    def add_translation(self, name, values):
        for param in self._params:
            if param.name == name:
                if len(param.values) != len(values):
                    raise Exception('Parameter {0} has {1} values, but {2} translations'.format(name, len(param.values), len(values)))
                self._translations[name] = {}
                for (p, v) in zip(param.values, values):
                    self._translations[name][p] = v
                return

        raise Exception('Parameter {0} is required before any translations for it'.format(name))

    def add_fields(self, names):
        for (field, original, values) in self._expand_names([(name, name, None) for name in names], self._params):
            if field not in self._fields:
                self._fields.append(field)

    def add_templates(self, names, deck=None):
        if self._note and self._note.cloze:
            raise Exception('cards cannot be added to a cloze note type')

        front = {}
        back = {}

        for name in names:
            front[name] = self._datasource.read(['config', 'templates', self._note.name], name + '.front')
            back[name] = self._datasource.read(['config', 'templates', self._note.name], name + '.back')

        for (name, original, values) in self._expand_names([(name, name, None) for name in names], self._params):
                if name not in [t.name for t in self._templates]:
                    f = self._replace_parameter_values(front[original], values)
                    b = self._replace_parameter_values(back[original], values)
                    self._templates.append(Template(name, deck, f, b))

    def create(self):
        notetype = self._course.get_alias(self._note.name)
        if notetype:
            for template in self._templates:
                if template.deck:
                    template.deck = self._course.get_alias(template.deck)
            createModel(notetype, self._note.cloze, self._note.css, self._fields, self._templates)

    def edit(self):
        notetype = self._course.get_alias(self._note.name)
        if notetype:
            for template in self._templates:
                if template.deck:
                    template.deck = self._course.get_alias(template.deck)
            editModel(notetype, self._note.css, self._fields, self._templates)

    def _expand_names(self, names, params):
        if not len(params):
            return names

        # expand last param
        expanded = []
        param = params[-1]
        for value in param.values:
            for (name, original, values) in names:
                if _matches(param.name, name):
                    values = {} if values is None else dict(values)
                    values[param.name] = value
                    v = _replace(name, param.name, value)
                    if v not in expanded:
                        expanded.append((v, original, values))
                else:
                    expanded.append((name, original, values))

        # expand other params in a recursive call
        return self._expand_names(expanded, params[:-1])

    def _replace_parameter_values(self, s, values):
        if values is not None:
            for name in values:
                value = values[name]
                # replace translations first
                if name in self._translations and _matches(name, s, '$$'):
                    s = _replace(s, name, self._translations[name][value], '$$')
                s = _replace(s, name, value)
        return s

def _matches(param, s, prefix='$'):
    return prefix + '{' + param + '}' in s or prefix + param in s

def _replace(s, name, value, prefix='$'):
    if s:
        s = s.replace(prefix + '{' + name + '}', value)
        s = s.replace(prefix + name, value)
    return s
    