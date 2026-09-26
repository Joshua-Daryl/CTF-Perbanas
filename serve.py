import os
import sys

# Force import driver PostgreSQL di top-level agar dibundel penuh oleh Vercel
try:
    import pg8000
except ImportError:
    pass

# 1. Paksa Override Folder Read-Write ke /tmp untuk Vercel Serverless (Mencegah Errno 30)
# Gunakan SimpleCache (RAM) agar tidak mengandalkan disk I/O di Serverless
os.environ["CACHE_TYPE"] = "SimpleCache"
os.environ["CACHE_DIR"] = "/tmp/.data"
os.environ["UPLOAD_FOLDER"] = "/tmp/uploads"

# 2. Ambil Argumen jika Dijalankan via CLI (Bypass argparse jika Di-import oleh Vercel)
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--port", help="Port for debug server to listen on", default=4000)
parser.add_argument(
    "--profile", help="Enable flask_profiler profiling", action="store_true"
)
parser.add_argument(
    "--disable-gevent",
    help="Disable importing gevent and monkey patching",
    action="store_true",  # gevent TIDAK aktif secara default di Vercel
)

# Parse argumen tanpa crash saat di-import oleh serverless handler Vercel
args, _ = parser.parse_known_args()

# Disable gevent secara penuh di Vercel untuk mencegah RuntimeError greenlet
if not os.environ.get("VERCEL") and not args.disable_gevent:
    try:
        print(" * Importing gevent and monkey patching. Use --disable-gevent to disable.")
        from gevent import monkey
        monkey.patch_all()
    except Exception as e:
        print(f" * Gevent monkey patching skipped: {e}")

# 3. Import CTFd setelah environment & monkey patch disiapkan
from CTFd import create_app

app = create_app()

if args.profile:
    try:
        from flask_debugtoolbar import DebugToolbarExtension  # type: ignore
        import flask_profiler  # type: ignore

        app.config["flask_profiler"] = {
            "enabled": app.config["DEBUG"],
            "storage": {"engine": "sqlite"},
            "basicAuth": {"enabled": False},
            "ignore": ["^/themes/.*", "^/events"],
        }
        flask_profiler.init_app(app)
        app.config["DEBUG_TB_PROFILER_ENABLED"] = True
        app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

        toolbar = DebugToolbarExtension()
        toolbar.init_app(app)
    except ImportError:
        pass

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host="127.0.0.1", port=args.port)