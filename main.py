"""Runs arxiv-search in debug mode.

Run as `python main.py`"""
from feed.factory import create_web_app

if __name__ == "__main__":
    app = create_web_app()
    app.config['FLASK_DEBUG']=1
    app.config['DEBUG']=1
    app.run(debug=True, port=8080)
