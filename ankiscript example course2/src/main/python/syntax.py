
import ankiscript.syntax as default_syntax
from ankiscript.command import command
from ankiscript.registery import CommandRegistery
from anki.utils import stripHTMLMedia

#
# called by Parser to init syntax parsing
# this syntax defaults to the original syntax if a line is not recognised as a custom command
#
def init(parser):
    parser.add_syntax(lambda line, **kwargs: CommandRegistery.find().parse(line, **kwargs))
    default_syntax.init(parser)


#
# this is a custom multiline command split after 'with'
# - note that the custom syntax is designed such that the subcommands just need the verb preprending to form one of the standalone commands
#
@command(r'verb {russian} [{audio}] (to {english}) with {commands}')
def _verb(russian, audio, english, commands, **kwargs):
    _infinitive(russian, english, audio, **kwargs)
    for cmd in commands.split(';'):
        cmd = cmd.strip()
        kwargs['parser'].parse_line(russian + ' ' + cmd, **kwargs)

@command(r'verb {russian} [{audio}] - to {english}')
def _infinitive_with_audio(russian, audio, english, **kwargs):
    _infinitive(russian, english, audio, **kwargs)

@command(r'verb {russian} - to {english}')
def _infinitive_no_audio(russian, english, **kwargs):
    _infinitive(russian, english, **kwargs)

@command(r'{russian} present tense: {я}, {ты}, {он}, {мы}, {вы}, {они}')
def _present_tense(russian, я, ты, он, мы, вы, они, **kwargs):
    cmd = 'for verb {0} set fields "Russian (я)" to {1}, "Russian (ты)" to {2}, "Russian (он/она/оно)" to {3}, "Russian (мы)" to {4}, "Russian (вы)" to {5}, "Russian (они)" to {6}'.format(russian, я, ты, он, мы, вы, они)
    kwargs['parser'].parse_line(cmd, **kwargs)

@command(r'{russian} past tense ({english}): {m}, {f}, {n}, {pl}')
def _past_tense(russian, english, m, f, n, pl, **kwargs):
    cmd = 'for verb {0} set fields "English (past)" to {1}, "Russian (past, m)" to {2}, "Russian (past, f)" to {3}, "Russian (past, n)" to {4}, "Russian (past, pl)" to {5}'.format(russian, english, m, f, n, pl)
    kwargs['parser'].parse_line(cmd, **kwargs)

@command(r'{russian} {aspect} (pair {pair})')
def _aspect(russian, aspect, pair, **kwargs):
    cmd = 'for verb {0} set fields Aspect to {1}, Pair to {2}'.format(russian, aspect, pair)
    kwargs['parser'].parse_line(cmd, **kwargs)


def _infinitive(russian, english, audio=None, **kwargs):
    cmd = 'add verb note, setting fields Russian to {0}, English to "to {1}"'.format(russian, english)
    if audio:
        cmd = cmd + ', Audio to "[sound:{0}.{1}]"'.format(stripHTMLMedia(russian), audio)
    kwargs['parser'].parse_line(cmd, **kwargs)
