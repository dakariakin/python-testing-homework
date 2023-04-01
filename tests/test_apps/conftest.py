import datetime as dt
import pytest
from typing import TypedDict, final
from mimesis import Field, Schema
from mimesis.enums import Locale
from server.apps.identity.models import User


class UserData(TypedDict, total=False):
    """
    Represent the simplified user data that is required to create a new user.
    It does not include ``password``, because it is very special in django.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    email: str
    first_name: str
    last_name: str
    date_of_birth: dt.datetime
    address: str
    job_title: str
    phone: str
    phone_type: int
    password: str


@final
class RegistrationData(UserData, total=False):
    """
    Represent the registration data that is required to create a new user.
    Importing this type is only allowed under ``if TYPE_CHECKING`` in tests.
    """
    password1: str
    password2: str


@final
class LoginData(TypedDict, total=False):
    """Represent the simplified login data."""

    username: str
    password: str


@pytest.fixture()
def user_data_factory():
    """Returns factory for fake random data for registration."""

    def factory(faker_seed, **fields) -> RegistrationData:
        mf = Field(locale=Locale.RU, seed=faker_seed)
        password = mf('password')  # by default passwords are equal
        schema = Schema(schema=lambda: {
            'email': mf('person.email'),
            'first_name': mf('person.first_name'),
            'last_name': mf('person.last_name'),
            'date_of_birth': mf('datetime.date'),
            'address': mf('address.city'),
            'job_title': mf('person.occupation'),
            'phone': mf('person.telephone'),
        })
        return {
            **schema.create(iterations=1)[0],  # type: ignore[misc]
            **{'password': password},
            **fields,
        }

    return factory


@pytest.fixture()
def user_data(user_data_factory, faker_seed):
    """Random user data from factory."""
    return user_data_factory(faker_seed)


@pytest.fixture()
def registration_data(user_data: RegistrationData) -> RegistrationData:
    """Registration user data."""
    user_data['password1'] = user_data['password']
    user_data['password2'] = user_data['password']

    return user_data


@pytest.fixture()
def login_data(user_data: UserData) -> LoginData:
    """Login data"""
    return {
        'username': user_data['email'],
        'password': user_data['password'],
    }


@pytest.mark.django_db()
@pytest.fixture()
def saved_user(user_data: UserData) -> User:
    """Create new user in the db."""
    user = User(**user_data)
    user.set_password(user_data['password'])
    user.save()

    return user


@pytest.fixture(scope='session')
def assert_correct_user():
    """Check that user created correctly."""

    def factory(expected: RegistrationData) -> None:
        user = User.objects.get(email=expected['email'])
        # Special fields:
        assert user.id
        assert user.is_active
        assert not user.is_superuser
        assert not user.is_staff
        # All other fields:
        for field_name, data_value in expected.items():
            if not field_name.startswith('password'):
                assert getattr(user, field_name) == data_value

    return factory
