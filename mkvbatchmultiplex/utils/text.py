"""
Text strings used in the application
"""

def ngettext(s1, s2, n): # pylint: disable=invalid-name
    """Dummy"""
    return s1 + s2 + str(n)

class Text():
    """
    Text strings used in the application
    """
    def __init__(self, initText):

        if initText:
            del globals()['ngettext']

    S_ = lambda s: s

    n = 0

    txt0001 = S_('Match')
    txt0002 = S_('Search')
    txt0003 = S_('Find All')
    txt0004 = lambda n: ngettext('Substitution', 'Substitutions', n)
    txt0005 = S_('Regular expression')
    txt0006 = S_('Enter regular expression.')
    txt0007 = S_('Substitution string')
    txt0008 = S_('Enter substitution string.')
    txt0009 = S_('Enter text')
    txt0010 = S_('Enter text to scan.')
    txt0011 = S_('Bad regular expression.')
    txt0012 = S_('Match results output.')
    txt0013 = S_("Regular Expressions Tool")
    txt0014 = S_("Exit Application")
    txt0015 = S_("Ctrl+E")
    txt0016 = S_('Confirm restore ...')
    txt0017 = S_("Abort")
    txt0018 = S_("Force exit")
    txt0019 = S_("Enable logging")
    txt0020 = S_("Enable session logging in {}")
    txt0021 = S_("Font && size")
    txt0022 = S_("Select font & size")
    txt0023 = S_("Restore defaults")
    txt0024 = S_("Using")
    txt0025 = S_("&Help")
    txt0026 = S_("&File")
    txt0027 = S_("&Settings")
    txt0028 = S_("&Interface language")
    txt0029 = S_("Exit")
    txt0030 = S_("&Exit")
    txt0031 = S_("Yes")
    txt0032 = S_("Are you sure you want to exit?")
    txt0033 = S_("Close App")
    txt0034 = lambda n: ngettext('Result', 'Results', n)
    txt0035 = lambda n: ngettext('Matched Group', 'Matched Groups', n)
    txt0036 = S_('Restore default settings?')
    txt0037 = S_('Author')
    txt0038 = S_('email')
    txt0039 = S_('Python Version')
    txt0040 = S_('About regExpressions')
    txt0041 = S_('Undo')
