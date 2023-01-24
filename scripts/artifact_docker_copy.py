import os
import argparse
import subprocess

root_dir = "/sam-artifact/sam/"
OUTPUT_DIR = "OUTPUT_DIR"

files_to_copy = {
    "blocks_sf.pdf": "fig13a.pdf",
    "fusion.pdf": "fig13b.pdf",
    "urandom_const_sf.pdf": "fig13c.pdf",
    "reorder.pdf": "fig14a.pdf",
    "runs_sf.pdf": "fig14b.pdf",
}

def docker_copy(docker_id, fp, output_dir):

    docker_cp_command = ['docker', 'cp', f'{docker_id}:{fp}', f'{output_dir}']
    ret_code = subprocess.run(docker_cp_command)
    print(ret_code)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Copy out figs/results from Docker container')
    parser.add_argument("--docker_id", type=str, default=None)
    parser.add_argument("--output_dir", type=str, default=None)
    args = parser.parse_args()

    did_ = args.docker_id
    od_ = args.output_dir

    assert did_ is not None
    assert od_ is not None

    if not os.path.isdir(od_):
        os.makedirs(od_)

    for file_in_, file_out_ in files_to_copy.items():
        synth_path = os.path.join(root_dir, OUTPUT_DIR, file_in_)
        out_p = os.path.join(od_, file_out_)
        docker_copy(did_, synth_path, od_)