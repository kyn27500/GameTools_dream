#!/bin/bash
cd /root/work/client/GameTools_dream
forever -w -a start -l forever.log -o out.log -e err.log bin/www