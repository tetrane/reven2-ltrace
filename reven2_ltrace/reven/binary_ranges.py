"""Get binary ranges from the reven trace using the search service
"""

import reven_api as _reven_api


# modified from API to take a simple binary path string instead of Ossi.Binary
def _binary_criterion(binary_path):
    criterion = _reven_api.criterion()
    criterion.type = _reven_api.criterion_type.binary
    criterion.accuracy = _reven_api.criterion_accuracy.exact
    criterion.effect = _reven_api.criterion_effect.match
    criterion.case_sensitive = False
    criterion.pattern = binary_path
    return criterion


def _search_once(trace, criteria, from_context, to_context):
    search_range = trace.search._search_range(from_context, to_context)

    request = _reven_api.search_request()
    request.max_sequences = 300000
    request.max_results = 1
    request.forward = True
    request.need_all = True
    for crit in criteria:
        request.criteria.append(crit)

    while search_range.begin() != search_range.end():
        results = trace._rvn.run_search_sequences(search_range, request)
        for match in results.content:
            return trace.context_before(match.transition_id)
        search_range = results.remaining_range

    return None


def _previous_context(ctxt):
    return ctxt - 1


def _last_context(trace):
    return trace.context_after(trace.transition_count - 1)


def enter_binary(trace, path, from_context=None, to_context=None):
    crit = _binary_criterion(path)
    crit.effect = _reven_api.criterion_effect.match
    return _search_once(trace, [crit], from_context, to_context)


def leave_binary(trace, path, from_context=None, to_context=None):
    crit = _binary_criterion(path)
    crit.effect = _reven_api.criterion_effect.invert_match
    return _search_once(trace, [crit], from_context, to_context)


def binary_ranges(trace, path, from_context=None, to_context=None):
    """Generate context ranges (first, last_included) for given binary."""
    first = enter_binary(trace, path, from_context, to_context)
    while first is not None:
        last = leave_binary(trace, path, first, to_context)

        if last is None:
            last = (
                _last_context(trace)
                if to_context is None
                else _previous_context(to_context)
            )
            yield (first, last)
            break

        if last == first:
            # didn't leave binary. might happen if binary is '<unknown>'
            break

        yield (first, _previous_context(last))
        first = enter_binary(trace, path, last, to_context)
