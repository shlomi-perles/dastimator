from pygments.style import Style
from pygments.token import Comment, Error, Generic, Keyword, Literal, Name, Operator, Text, Punctuation


class DarculaStyle(Style):
    """
    Pygments color scheme inspired by the darcula theme (Pycharm/IntelliJ Idea)
    imported from pyqodeng
    """
    background_color = '#111111'
    highlight_color = '#333333'

    styles = {
        Comment.Multiline: ' #808080',
        Comment.Preproc: '#808080',
        Comment.Single: ' #808080',
        Comment.Special: 'bold  #808080',
        Comment: ' #808080',
        Error: '#CC0000',
        Generic.Deleted: '#CC4040',
        Generic.Emph: ' #A9B7C6',
        Generic.Error: '#aa0000',
        Generic.Heading: '#999999',
        Generic.Inserted: '#40CC40',
        Generic.Output: '#888888',
        Generic.Prompt: '#555555',
        Generic.Strong: 'bold',
        Generic.Subheading: '#aaaaaa',
        Generic.Traceback: '#aa0000',
        Keyword.Constant: '#CC7832 ',
        Keyword.Declaration: '#CC7832',
        Keyword.Namespace: '#CC7832',
        Keyword.Pseudo: '#CC7832',
        Keyword.Reserved: '#CC7832',
        Keyword.Type: '#A9B7C6 bold',
        Keyword: '#CC7832 bold',
        Literal.Number: '#6897B3',
        Literal.String: '#008080 ',
        Literal.String.Doc: '#629755 ',
        Name.Attribute: '#800080',
        Name.Builtin.Pseudo: '#94558D',
        Name.Builtin: '#8888C6',
        Name.Class: '#A9B7C6 bold',
        Name.Constant: '#B200B2',
        Name.Decorator: '#BBB529',
        Name.Entity: '#A9B7C6',
        Name.Exception: '#A9B7C6 bold',
        Name.Function: '#A9B7C6 bold',
        Name.Label: '#A9B7C6 bold',
        Name.Namespace: '#A9B7C6',
        Name.Tag: '#A5C261 bold',
        Name.Variable.Class: '#A9B7C6 bold',
        Name.Variable.Global: '#A9B7C6 bold',
        Name.Variable.Instance: '#A9B7C6',
        Name.Variable: '#A9B7C6',
        Operator: '#808080 bold',
        Operator.Word: '#CC7832 bold',
        Text: '#A9B7C6',
        Text.Whitespace: '#656565',
        Punctuation: '#A9B7C6'
    }


def pygments_monkeypatch_style(mod_name, cls):
    import sys
    import pygments.styles
    cls_name = cls.__name__
    mod = type(__import__("os"))(mod_name)
    setattr(mod, cls_name, cls)
    setattr(pygments.styles, mod_name, mod)
    sys.modules["pygments.styles." + mod_name] = mod
    from pygments.styles import STYLE_MAP
    STYLE_MAP[mod_name] = mod_name + "::" + cls_name
