#!/bin/bash

base_path="$SUBMS_BASE_PATH"


if [  -z "$base_path" ]; then
    subm_path="$1"
    ./bin/submission_checker v3 -a "$subm_path"
    exit $?
fi

subm_dir="$1"
shopt -s extglob
./bin/submission_checker v3 -a $base_path/$subm_dir/*@(.rar|.zip|.tar.gz)
