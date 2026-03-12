#!/bin/bash
git pull --rebase origin main
git add .
git commit -m "${1:-update}"
git push origin main
