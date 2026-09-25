"""Command line:

    python -m violence_detection analyze clip.mp4 [--weights weights/]
    python -m violence_detection serve [--port 5000]
"""

import argparse
import json
import os
import sys


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="violence_detection")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("analyze", help="analyse one video file")
    a.add_argument("video")
    a.add_argument("--weights", default=os.environ.get("VD_WEIGHTS_DIR", "weights"))
    s = sub.add_parser("serve", help="run the HTTP API")
    s.add_argument("--port", type=int, default=5000)
    s.add_argument("--host", default="127.0.0.1")
    args = p.parse_args(argv)

    if args.cmd == "analyze":
        from .cascade import Cascade
        from .models import load_trained
        audio_fn, video_fn = load_trained(args.weights)
        print(json.dumps(Cascade(audio_fn, video_fn).analyse(args.video).to_dict(), indent=2))
        return 0

    from .api import create_app
    create_app().run(host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
