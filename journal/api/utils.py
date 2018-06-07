from jsondiff import diff as _diff


def _make_diff(dict1, dict2):
    diff = _diff(dict1, dict2, syntax='explicit')
    return diff


def _invert_diff(dict1, dict2, diff):
    keys = list(diff.keys())
    inverted = {}
    for k in keys:
        original_entry = diff[k]
        for f in original_entry.keys():
            field, action, value = f, k.label, original_entry[f]
            if type(value) == dict:
                resolved_action_for_field = _resolve_inner_actions(dict1, f, value)
                inverted[field] = resolved_action_for_field
            else:
                inverted[field] = {action: value}
    return inverted


def _resolve_inner_actions(dict_from, comparable_field, value):
    resolved_action_for_field = {}
    for k,v in value.items():
        action = k.label
        value = v
        if type(value) == list:
            value_list = []
            if action == 'delete':
                # {delete: [2]} only indexes
                for i in value:
                    value_list.append(dict_from[comparable_field][i])
            elif action == 'insert':
                # {insert: [(1, 'b'), (2, 'c')]} - index with value
                for i in value:
                    value_list.append(i[1])
            resolved_action_for_field[action] = value_list
    return resolved_action_for_field


def make_diff(dict1, dict2):
    """
    Make difference's dict in format field:{action:value}
    """
    diff = _make_diff(dict1, dict2)
    invert_diff = _invert_diff(dict1, dict2, diff)
    return invert_diff