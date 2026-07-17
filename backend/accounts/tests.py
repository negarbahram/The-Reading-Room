import pytest

from accounts.models import User


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_member(self, api_client):
        resp = api_client.post('/api/v1/auth/register/', {
            'email': 'new@test.com', 'password': 'StrongPass123', 'first_name': 'New', 'last_name': 'User',
        })
        assert resp.status_code == 201
        assert resp.data['user']['role'] == 'MEMBER'
        assert 'token' in resp.data
        assert User.objects.get(email='new@test.com').role == User.Role.MEMBER

    def test_register_duplicate_email_fails(self, api_client, member):
        resp = api_client.post('/api/v1/auth/register/', {
            'email': member.email, 'password': 'StrongPass123',
        })
        assert resp.status_code == 400

    def test_register_cannot_self_assign_admin_role(self, api_client):
        resp = api_client.post('/api/v1/auth/register/', {
            'email': 'wannabe-admin@test.com', 'password': 'StrongPass123', 'role': 'ADMIN',
        })
        assert resp.status_code == 201
        assert User.objects.get(email='wannabe-admin@test.com').role == User.Role.MEMBER


@pytest.mark.django_db
class TestLoginLogout:
    def test_login_success(self, api_client, member):
        resp = api_client.post('/api/v1/auth/login/', {'email': member.email, 'password': 'pass12345'})
        assert resp.status_code == 200
        assert 'token' in resp.data

    def test_login_wrong_password(self, api_client, member):
        resp = api_client.post('/api/v1/auth/login/', {'email': member.email, 'password': 'wrong'})
        assert resp.status_code == 400

    def test_logout_deletes_token(self, api_client, member):
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=member)
        api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        resp = api_client.post('/api/v1/auth/logout/')
        assert resp.status_code == 204
        assert not Token.objects.filter(user=member).exists()


@pytest.mark.django_db
class TestPermissions:
    def test_anonymous_cannot_access_private_route(self, api_client):
        resp = api_client.get('/api/v1/users/me/')
        assert resp.status_code == 401

    def test_member_cannot_access_admin_user_list(self, member_client):
        resp = member_client.get('/api/v1/users/')
        assert resp.status_code == 403

    def test_admin_can_access_admin_user_list(self, admin_client):
        resp = admin_client.get('/api/v1/users/')
        assert resp.status_code == 200

    def test_member_cannot_escalate_own_role(self, member_client, member):
        resp = member_client.patch(f'/api/v1/users/{member.id}/', {'role': 'ADMIN'})
        assert resp.status_code == 403
        member.refresh_from_db()
        assert member.role == User.Role.MEMBER

    def test_admin_can_suspend_member(self, admin_client, member):
        resp = admin_client.patch(f'/api/v1/users/{member.id}/', {'is_suspended': True})
        assert resp.status_code == 200
        member.refresh_from_db()
        assert member.is_suspended is True
