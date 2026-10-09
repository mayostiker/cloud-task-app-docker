
from unittest.mock import MagicMock, patch

from dotenv import load_dotenv

load_dotenv()

from app import app


TEST_USER_ID = 2


def authenticated_client():
    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = TEST_USER_ID
        session["username"] = "moses"

    return client


def test_home_page():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_cursor.fetchall.return_value = [
        {
            "id": 1,
            "title": "Learn Docker",
            "completed": False,
            "created_at": "2026-10-06 20:00:00",
        }
    ]
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.get("/")

    assert response.status_code == 200
    assert b"Cloud Task App" in response.data
    assert b"Learn Docker" in response.data

    mock_cursor.execute.assert_called_once_with(
        """
            SELECT id, title, completed, created_at
            FROM tasks
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
        (TEST_USER_ID,),
    )


def test_add_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.post(
            "/add",
            data={"task": "Practice CI/CD"},
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO tasks (user_id, title) VALUES (%s, %s)",
        (TEST_USER_ID, "Practice CI/CD"),
    )
    mock_connection.commit.assert_called_once()


def test_complete_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.post("/complete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        """
            UPDATE tasks
            SET completed = TRUE
            WHERE id = %s AND user_id = %s
            """,
        (1, TEST_USER_ID),
    )
    mock_connection.commit.assert_called_once()


def test_delete_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.post("/delete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM tasks WHERE id = %s AND user_id = %s",
        (1, TEST_USER_ID),
    )
    mock_connection.commit.assert_called_once()


def test_home_redirects_when_logged_out():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


def test_add_redirects_when_logged_out():
    client = app.test_client()

    response = client.post("/add", data={"task": "Unauthorized task"})

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"


from werkzeug.security import check_password_hash


def test_register_page_loads():
    client = app.test_client()

    response = client.get("/register")

    assert response.status_code == 200
    assert b"Create an Account" in response.data


def test_register_creates_user_with_hashed_password():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post(
            "/register",
            data={
                "username": "newtester",
                "email": "newtester@example.com",
                "password": "TestPassword123!",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    executed_sql = mock_cursor.execute.call_args
    assert "INSERT INTO users" in executed_sql.args[0]
    assert executed_sql.args[1][0] == "newtester"
    assert executed_sql.args[1][1] == "newtester@example.com"

    stored_hash = executed_sql.args[1][2]
    assert stored_hash != "TestPassword123!"
    assert check_password_hash(stored_hash, "TestPassword123!")

    mock_connection.commit.assert_called_once()


def test_register_rejects_short_password():
    client = app.test_client()

    response = client.post(
        "/register",
        data={
            "username": "shortpass",
            "email": "shortpass@example.com",
            "password": "123",
        },
    )

    assert response.status_code == 400
    assert b"at least 8 characters" in response.data


def test_login_page_loads():
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert b"Welcome Back" in response.data


def test_login_success_creates_session():
    from werkzeug.security import generate_password_hash

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 2,
        "username": "moses",
        "password_hash": generate_password_hash("CorrectPassword123!"),
    }
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post(
            "/login",
            data={
                "username": "moses",
                "password": "CorrectPassword123!",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as session:
        assert session["user_id"] == 2
        assert session["username"] == "moses"


def test_login_rejects_incorrect_password():
    from werkzeug.security import generate_password_hash

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 2,
        "username": "moses",
        "password_hash": generate_password_hash("CorrectPassword123!"),
    }
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post(
            "/login",
            data={
                "username": "moses",
                "password": "WrongPassword123!",
            },
        )

    assert response.status_code == 401
    assert b"Invalid username or password" in response.data


def test_logout_clears_session():
    client = app.test_client()

    with client.session_transaction() as session:
        session["user_id"] = 2
        session["username"] = "moses"

    response = client.post("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "username" not in session


def test_complete_task_query_checks_user_ownership():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.post("/complete/7")

    assert response.status_code == 302

    mock_cursor.execute.assert_called_once_with(
        """
            UPDATE tasks
            SET completed = TRUE
            WHERE id = %s AND user_id = %s
            """,
        (7, TEST_USER_ID),
    )


def test_delete_task_query_checks_user_ownership():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = authenticated_client()
        response = client.post("/delete/7")

    assert response.status_code == 302

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM tasks WHERE id = %s AND user_id = %s",
        (7, TEST_USER_ID),
    )
