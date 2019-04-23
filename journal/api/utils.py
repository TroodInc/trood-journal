from jsondiff import diff as _diff


def _invert_diff(prev, new, diff):
    inverted = {}
    for action, value in diff.items():
        if action.label == 'delete':
            for deleted in value:
                inverted[deleted] = {action.label: prev[deleted]}

        elif action.label in ('insert', 'update'):
            for field, changes in value.items():
                if field in prev and type(prev[field]) == list:
                    changes = {k.label: v for k, v in changes.items()}

                    if 'insert' in changes:
                        changes['insert'] = [v[1] for v in changes['insert']]

                    if 'delete' in changes:
                        changes['delete'] = [prev[field][v] for v in changes['delete']]

                    inverted[field] = changes

                elif type(changes) == dict:
                    inverted[field] = {action.label: new[field]}
                else:
                    inverted[field] = {action.label: value[field]}

    return inverted


def make_diff(dict1, dict2):
    """
    Make difference's dict in format field:{action:value}
    """
    diff = _diff(dict1, dict2, syntax='explicit')
    print(diff)
    return _invert_diff(dict1, dict2, diff)
