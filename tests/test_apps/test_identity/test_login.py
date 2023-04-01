from http import HTTPStatus

import pytest
from django.test import Client


def test_login_unauthorized(client: Client) -> None:
    """This test ensures that login page is accessible."""
    response = client.get('/identity/login')

    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db()()
def test_login_authorized(client: Client) -> None:
    """This test ensures that login page is accessible."""
    response = client.get('/identity/login')

    assert response.status_code == HTTPStatus.FOUND
