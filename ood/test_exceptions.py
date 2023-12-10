import pozo.ood.exceptions as e
import pytest

all_exceptions = [e.StrictIndexException,
                  e.NameConflictException,
                  e.MultiParentException,
                  e.RedundantAddException,
                  ]
all_messages = ["Invalid key or index.",
                "Can't add >1 {thing} with same name.",
                "{thing} can only have one parent.",
                "Trying to add duplicate {thing}.",
                ]

def test_existence():
    e.SelectorError()
    e.SelectorTypeError()
    e.NameConflictError()
    with pytest.raises(NotImplementedError):
        e.AdjustableException()
    e.StrictIndexException()
    e.RedundantAddException()
    e.MultiParentException()

@pytest.mark.parametrize("exception", all_exceptions)
def test_levels(exception):

    exception().notify(e.ErrorLevel.IGNORE)
    exception().notify(False)

    with pytest.raises(exception):
        exception().notify(e.ErrorLevel.ERROR)

    with pytest.raises(exception):
        exception().notify(True)

    with pytest.warns():
        exception().notify(e.ErrorLevel.WARN)


def test_default_levels():
    e.StrictIndexException().notify()

    with pytest.raises(e.NameConflictException):
        e.NameConflictException().notify()

    with pytest.raises(e.MultiParentException):
        e.MultiParentException().notify()

    with pytest.warns():
        e.RedundantAddException().notify()

@pytest.mark.parametrize("exception", zip(all_exceptions, all_messages))
def test_message_formating(exception):
    exception, message = exception[0], exception[1]
    formatted_item = message.format(thing="item")
    with pytest.warns(match=formatted_item):
        exception().notify(e.ErrorLevel.WARN)

    formatted_test = message.format(thing="test")
    with pytest.warns(match=formatted_test):
        exception("test").notify(e.ErrorLevel.WARN)



@pytest.mark.parametrize("exception", all_exceptions)
def test_change_defaults(exception):
    # NB: maybe better to use `pytest-xdist` and
    # `pytest --fork` to deal with globals
    # Good to be last test
    original_default = exception.default_level

    exception.default_level = e.ErrorLevel.IGNORE
    exception().notify()

    exception.default_level = e.ErrorLevel.ERROR
    with pytest.raises(exception):
        exception().notify()

    exception.default_level = e.ErrorLevel.WARN
    with pytest.warns():
        exception().notify()

    exception.default_level = original_default
