from unittest.mock import MagicMock, patch

from app import app


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
        client = app.test_client()
        response = client.get("/")

    assert response.status_code == 200
    assert b"Cloud Task App" in response.data
    assert b"Learn Docker" in response.data


def test_add_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post(
            "/add",
            data={"task": "Practice CI/CD"},
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO tasks (title) VALUES (%s)",
        ("Practice CI/CD",),
    )

    mock_connection.commit.assert_called_once()
def test_complete_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post("/complete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        "UPDATE tasks SET completed = TRUE WHERE id = %s",
        (1,),
    )

    mock_connection.commit.assert_called_once()
def test_delete_task():
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor

    with patch("app.get_connection", return_value=mock_connection):
        client = app.test_client()

        response = client.post("/delete/1")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM tasks WHERE id = %s",
        (1,),
    )

    mock_connection.commit.assert_called_once()
