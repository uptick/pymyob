def pluralise(s):
    if s.endswith('y'):
        return s[:-1] + 'ies'
    else:
        return s + 's'
