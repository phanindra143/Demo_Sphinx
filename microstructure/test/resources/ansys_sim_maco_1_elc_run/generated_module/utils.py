
import time
import os
from pathlib import Path

def wait_for_checkpoint_file(mapdl, checkpoint_file):
    ansys_workdir = mapdl.directory
    checkpoint_path = Path(ansys_workdir) / checkpoint_file
    if False:
        print(f"waiting for {checkpoint_path}")
    while not checkpoint_path.exists():
        time.sleep(0.1)
    os.remove(checkpoint_path)
