#!/bin/bash
git add .
git commit -m "${1:-update}"
git pull --rebase origin main
git push origin main
