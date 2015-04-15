__all__ = ['parse_name']


def parse_name(name):
    """
    >>> parse_name('repo:tag')
    ('repo', 'tag')
    >>> parse_name('rep/o:tag')
    ('rep/o', 'tag')
    >>> parse_name('repo/tag')
    ('repo/tag', None)
    >>> parse_name('re:po/tag')
    ('re:po/tag', None)
    """
    img, tag = name, None
    if ':' in name:
        a, b = name.rsplit(':', 1)
        if '/' not in b:
            img, tag = a, b
    return img, tag
