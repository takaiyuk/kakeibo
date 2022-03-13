#!/bin/bash
function remove_dir () {
    if [ -d "$1" ]; then
        rm -r "$1"
    fi
}

remove_dir .mypy_cache
remove_dir .pytest_cache
remove_dir kakeibo/__pycache__
