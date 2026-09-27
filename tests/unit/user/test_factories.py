import pytest
from flask_login import login_user

from flaskbb.user.services import factories
from flaskbb.user.services.update import (
    DefaultDetailsUpdateHandler,
    DefaultEmailUpdateHandler,
    DefaultPasswordUpdateHandler,
    DefaultSettingsUpdateHandler,
)


@pytest.fixture(autouse=True)
def setup_request(user, default_settings, post_request_context):
    login_user(user)


def test_settings_update_handler_factory_returns_handler():
    handler = factories.settings_update_handler()

    assert isinstance(handler, DefaultSettingsUpdateHandler)


def test_details_update_factory_returns_handler(mocker):
    mock_validator = mocker.patch(
        "flaskbb.user.services.factories.pluggy.hook."
        "flaskbb_gather_details_update_validators",
        return_value=[],
    )

    handler = factories.details_update_factory()

    assert isinstance(handler, DefaultDetailsUpdateHandler)
    mock_validator.assert_called_once()


def test_password_update_handler_returns_handler(mocker):
    mocker.patch(
        "flaskbb.user.services.factories.pluggy.hook."
        "flaskbb_gather_password_validators",
        return_value=[],
    )

    handler = factories.password_update_handler()

    assert isinstance(handler, DefaultPasswordUpdateHandler)


def test_email_update_handler_returns_handler(mocker):
    mocker.patch(
        "flaskbb.user.services.factories.pluggy.hook."
        "flaskbb_gather_email_validators",
        return_value=[],
    )

    handler = factories.email_update_handler()

    assert isinstance(handler, DefaultEmailUpdateHandler)


def test_settings_form_factory_adds_default_theme(mocker):
    mocker.patch(
        "flaskbb.user.services.factories.get_available_themes",
        return_value=[("dark", "Dark")],
    )
    mocker.patch(
        "flaskbb.user.services.factories.get_available_languages",
        return_value=[("en", "English")],
    )

    form = factories.settings_form_factory()

    assert ("", "Default") in form.theme.choices


def test_settings_form_factory_loads_available_languages(mocker):
    mocker.patch(
        "flaskbb.user.services.factories.get_available_themes",
        return_value=[],
    )
    mocker.patch(
        "flaskbb.user.services.factories.get_available_languages",
        return_value=[("pt", "Português")],
    )

    form = factories.settings_form_factory()

    assert form.language.choices == [("pt", "Português")]


@pytest.mark.parametrize(
    "submitted, valid, uses_current_settings",
    [
        (False, False, True),
        (False, True, True),
        (True, False, True),
        (True, True, False),
    ],
)
def test_settings_form_factory_uses_current_settings_when_needed(
    mocker, user, submitted, valid, uses_current_settings
):
    from types import SimpleNamespace

    form = SimpleNamespace(
        theme=SimpleNamespace(choices=[], data=None),
        language=SimpleNamespace(choices=[], data=None),
    )
    form.is_submitted = mocker.Mock(return_value=submitted)
    form.validate_on_submit = mocker.Mock(return_value=valid)

    mocker.patch(
        "flaskbb.user.services.factories.GeneralSettingsForm",
        return_value=form,
    )
    mocker.patch(
        "flaskbb.user.services.factories.get_available_themes",
        return_value=[("dark", "Dark")],
    )
    mocker.patch(
        "flaskbb.user.services.factories.get_available_languages",
        return_value=[("pt", "Português")],
    )

    factories.settings_form_factory()

    if uses_current_settings:
        assert form.theme.data == user.theme
        assert form.language.data == user.language
    else:
        assert form.theme.data is None
        assert form.language.data is None
