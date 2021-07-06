def pluralise(s):
    if s.endswith('y'):
        return s[:-1] + 'ies'
    elif s.endswith('rix'):
        return s[:-1] + 'ces'
    else:
        return s + 's'
