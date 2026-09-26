import os
import sys

# Top-level import wajib agar terdeteksi Vercel AST parser
import pg8000

os.environ["CACHE_TYPE"] = "SimpleCache"
os.environ["CACHE_DIR"] = "/tmp/.data"
os.environ["UPLOAD_FOLDER"] = "/tmp/uploads"

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Port for debug server to listen on", default=4000)
parser.add_argument("--profile", help="Enable flask_profiler profiling", action="store_true")
parser.add_argument("--disable-gevent", help="Disable gevent", action="store_true")

args, _ = parser.parse_known_args()

from CTFd import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="127.0.0.1", port=args.port)