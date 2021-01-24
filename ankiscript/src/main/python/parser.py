
import traceback
from aqt import mw
from aqt.utils import showWarning
from .datasource import get_datasource


class Parser:

    @staticmethod
    def parse(source, course, syntax=None, description=None):
        with get_datasource(source) as datasource:
            with Parser(course, datasource, syntax) as parser:
                if course:
                    action = '{0} {1} update'.format(course.name, description) if description else '{0} update'.format(course.name)
                else:
                    action = '{0} ad-hoc script execution'.format(description) if description else 'ad-hoc script execution'
                return parser.execute(action)


    def __init__(self, course, datasource, syntax=None):
        self._syntax = []
        self.course = course
        self.datasource = datasource
        self._commands = []
        self._warnings = []

        # if no custom sytanx supplied use the default
        if syntax is None:
            from .syntax import init
            init(self)
        else:
            syntax(self)

    def __enter__(self):
        self._commands = []
        self._warnings = []

        cmd = ''
        for line in self.datasource.read([], 'commands.txt').split('\n'):
            line = line.strip()
            if line != '':
                cmd = cmd + ' ' + line if len(cmd) else line
            
            # commands may be split across multi lines for legibility
            if line.endswith(',') or line.endswith(';'):
                continue
            elif line.endswith(':'):
                cmd = cmd[:-1]
            else:
                self._commands.append(cmd)
                cmd = ''
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._commands = []
        return False

    def __iter__(self):
        return self._commands.__iter__()

    def add_syntax(self, syntax):
        self._syntax.append(syntax)

    def add_warning(self, warning):
        self._warnings.append(warning)

    def execute(self, action):
        mw.checkpoint(action)

        for cmd in self:
            try:
                self._parse(cmd, course=self.course, datasource=self.datasource)
            except Exception as x:
                msg = 'Undoing {0} due to error "{1}"'.format(action, x)
                if hasattr(x, 'cmd'):
                    msg = msg + '\n\nWas processing command:\n{0}'.format(x.cmd) 
                msg = msg + '''

------------------------------------------------------------------
Please include the information below if reporting an error
------------------------------------------------------------------

{0}'''.format(traceback.format_exc())
                showWarning(msg, title=self.course.name)
                mw.onUndo()
                return False

        if self._warnings:
            showWarning('\n'.join(self._warnings))

        # refresh main view so changes are visible
        mw.reset()
        return True

    def parse_line(self, cmd, **kwargs):
        for syntax in self._syntax:
            kwargs['parser'] = self
            if syntax(cmd, **kwargs):
                return True
        return False

    def _parse(self, cmd, **kwargs):
        try:
            if not self.parse_line(cmd, **kwargs):
                self._warnings.append('Unrecognized command: {0}'.format(cmd))
        except Exception as x:
            x.cmd = cmd
            raise x
