from api.main import start_server, app

def test_start_server(mocker):
	mock_start = mocker.patch("uvicorn.run", autospec=True)

	start_server()

	mock_start.assert_called_once_with(app, host="127.0.0.1", port=8000)
