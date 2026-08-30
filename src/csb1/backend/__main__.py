from __future__ import annotations

import os

from .app import create_app


def main() -> None:
    app, socketio = create_app()
    config = app.config["CSB1_CONFIG"]
    server = config["server"]
    socketio.run(
        app,
        host=server["host"],
        port=server["port"],
        debug=os.environ.get("FLASK_DEBUG") == "1",
        allow_unsafe_werkzeug=True,
    )


if __name__ == "__main__":
    main()

