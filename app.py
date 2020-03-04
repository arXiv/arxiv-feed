"""Provides application for development purposes."""

from feed.factory import create_web_app

app = create_web_app()

# Needed to allow debugging in PyCharm
if __name__ == "__main__":
    app.run(
        debug=True,
        use_debugger=False,
        use_reloader=False,
        passthrough_errors=True,
    )
