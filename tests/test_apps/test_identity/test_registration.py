from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from tests.test_apps.conftest import LoginData, RegistrationData


def test_registration_page_opens(client: Client) -> None:
    """This test ensures that registration page is accessible."""
    response = client.get(reverse('identity:registration'))

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db()
def test_registration_authorized(client: Client, saved_user) -> None:
    """This test ensures that we redirect authorized user from the page."""
    client.force_login(saved_user)
    response = client.get('/identity/registration')

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db()
def test_valid_registration(client: Client,
                            registration_data: RegistrationData,
                            assert_correct_user
                            ) -> None:
    response = client.post(
        reverse('identity:registration'),
        data=registration_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('identity:login')
    assert_correct_user(registration_data)


@pytest.mark.django_db()
def test_login(client: Client, login_data: LoginData):
    response = client.post(
        reverse('identity:login'),
        data=login_data,
    )
    assert response.status_code == HTTPStatus.FOUND
    assert response.get('Location') == reverse('pictures:dashboard')
