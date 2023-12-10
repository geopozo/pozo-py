import pozo.ood.exceptions as e
import pytest, contextlib

all_exceptions = [e.StrictIndexException,
                  e.NameConflictException,
                  e.MultiParentException,
                  e.RedundantAddException,
                  ]
all_messages = ["Invalid key or index.",
                "Can't add >1 {kind} with same name.",
                "{kind} can only have one parent.",
                "Trying to add duplicate {kind}.",
                ]
message_by_exception = {
        all_exceptions[i]: all_messages[i] for i in range(len(all_exceptions))
        }

def test_existence():
    e.SelectorError()
    e.SelectorTypeError()
    e.NameConflictError()
    with pytest.raises(NotImplementedError):
        e.AdjustableException()
    e.StrictIndexException()
    with pytest.warns():
        e.RedundantAddException()
    e.MultiParentException()

@pytest.mark.parametrize("exception", all_exceptions)
def test_levels(exception):

    err = exception(level=e.ErrorLevel.IGNORE)
    if err: raise err
    err = exception(level=False)
    if err: raise err

    with pytest.raises(exception):
        err = exception(level=e.ErrorLevel.ERROR)
        if err: raise err

    with pytest.raises(exception):
        err = exception(level=True)
        if err: raise err

    context = contextlib.nullcontext()
    if hasattr(exception, "no_warn"):
        context = pytest.raises(exception)
    with pytest.warns(), context:
        err = exception(level=e.ErrorLevel.WARN)
        if err: raise err


def test_default_levels():
    e.StrictIndexException()

    with pytest.raises(e.NameConflictException):
        err = e.NameConflictException()
        if err: raise err

    with pytest.raises(e.MultiParentException):
        err = e.MultiParentException()
        if err: raise err

    with pytest.warns():
        err = e.RedundantAddException()
        if err: raise err

@pytest.mark.parametrize("exception", message_by_exception)
def test_message_formating(exception):
    message = message_by_exception[exception]

    formatted_item = message.format(kind="item")
    main_context = pytest.warns(match=formatted_item)
    second_context = contextlib.nullcontext()
    if hasattr(exception, "no_warn"):
        main_context = pytest.raises(exception, match=formatted_item)
        second_context = pytest.warns()
    with main_context, second_context:
        err = exception(level=e.ErrorLevel.WARN)
        if err: raise err
    main_context = pytest.raises(exception, match=formatted_item)
    with main_context:
        err = exception(level=e.ErrorLevel.ERROR)
        if err: raise err

    formatted_test = message.format(kind="test")
    main_context = pytest.warns(match=formatted_test)
    second_context = contextlib.nullcontext()
    if hasattr(exception, "no_warn"):
        main_context = pytest.raises(exception, match=formatted_test)
        second_context = pytest.warns()
    with main_context, second_context:
        err = exception(kind="test", level=e.ErrorLevel.WARN)
        if err: raise err
    main_context = pytest.raises(exception, match=formatted_test)
    with main_context:
        err = exception(kind="test", level=e.ErrorLevel.ERROR)
        if err: raise err




@pytest.mark.parametrize("exception", all_exceptions)
def test_change_defaults(exception):
    # NB: maybe better to use `pytest-xdist` and
    # `pytest --fork` to deal with globals
    # Good to be last test
    original_default = exception.default_level

    exception.default_level = e.ErrorLevel.IGNORE
    err = exception()
    if err: raise err

    exception.default_level = e.ErrorLevel.ERROR
    with pytest.raises(exception):
        err = exception()
        if err: raise err

    exception.default_level = e.ErrorLevel.WARN
    context = contextlib.nullcontext()
    if hasattr(exception, "no_warn"):
        context = pytest.raises(exception)
    with pytest.warns(), context:
        err = exception()
        if err: raise err

    exception.default_level = original_default
