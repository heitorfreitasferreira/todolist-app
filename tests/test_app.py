# ABOUTME: Testes de fumaca da app (probes, auth, CRUD e cleanup).
# ABOUTME: Requer um Postgres acessivel (CI: service container; local: docker).
import pytest

from app import app, db, Todo


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def clean_db():
    with app.app_context():
        db.session.query(Todo).delete()
        db.session.commit()
    yield


def login(client):
    return client.post(
        '/login', data={'username': 'admin', 'password': 'admin'},
        follow_redirects=False)


def test_livez_nao_depende_do_banco(client):
    r = client.get('/livez')
    assert r.status_code == 200
    assert r.data == b'ok'


def test_healthz_ok_com_banco(client):
    assert client.get('/healthz').status_code == 200


def test_metrics_exposto(client):
    assert client.get('/metrics').status_code == 200


def test_root_exige_login(client):
    r = client.get('/')
    assert r.status_code == 302
    assert '/login' in r.headers['Location']


def test_login_recusa_credencial_errada(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'errada'})
    assert r.status_code == 200
    assert b'Invalid' in r.data


def test_crud_de_tarefa(client):
    assert login(client).status_code == 302

    r = client.post('/add', data={'task': 'comprar leite'}, follow_redirects=True)
    assert b'comprar leite' in r.data

    with app.app_context():
        todo = Todo.query.filter_by(task='comprar leite').one()
        assert todo.done is False
        tid = todo.id

    client.post(f'/toggle/{tid}')
    with app.app_context():
        assert db.session.get(Todo, tid).done is True

    client.post(f'/delete/{tid}')
    with app.app_context():
        assert db.session.get(Todo, tid) is None


def test_duplicada_rejeitada(client):
    login(client)
    client.post('/add', data={'task': 'repetida'})
    r = client.post('/add', data={'task': 'repetida'}, follow_redirects=True)
    assert b'already exists' in r.data


def test_cleanup_exige_token(client):
    assert client.post('/cleanup').status_code == 401
    r = client.post('/cleanup', headers={'X-Cleanup-Token': 'test-cleanup-token'})
    assert r.status_code == 200
    assert r.data.startswith(b'deleted ')
