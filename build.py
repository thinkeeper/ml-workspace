import argparse
import datetime
import subprocess

import docker
from universal_build import build_utils
from universal_build.helpers import build_docker

REMOTE_IMAGE_PREFIX = "civc/"
COMPONENT_NAME = "ml-workspace"

parser = argparse.ArgumentParser(add_help=False)

args = build_utils.parse_arguments(argument_parser=parser)

VERSION = str(args.get(build_utils.FLAG_VERSION))
docker_image_prefix = args.get(build_docker.FLAG_DOCKER_IMAGE_PREFIX)

if not docker_image_prefix:
    docker_image_prefix = REMOTE_IMAGE_PREFIX

build_utils.build(".", args)

docker_image_name = COMPONENT_NAME

# docker build
git_rev = "unknown"
try:
    git_rev = (
        subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
        .decode("ascii")
        .strip()
    )
except Exception:
    pass

build_date = datetime.datetime.utcnow().isoformat("T") + "Z"
try:
    build_date = (
        subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"])
        .decode("ascii")
        .strip()
    )
except Exception:
    pass

vcs_ref_build_arg = " --build-arg ARG_VCS_REF=" + str(git_rev)
build_date_build_arg = " --build-arg ARG_BUILD_DATE=" + str(build_date)
version_build_arg = " --build-arg ARG_WORKSPACE_VERSION=" + VERSION

if args[build_utils.FLAG_MAKE]:
    build_args = (
        version_build_arg
        + " "
        + vcs_ref_build_arg
        + " "
        + build_date_build_arg
    )

    completed_process = build_docker.build_docker_image(
        docker_image_name, version=VERSION, build_args=build_args
    )
    if completed_process.returncode > 0:
        build_utils.exit_process(1)
