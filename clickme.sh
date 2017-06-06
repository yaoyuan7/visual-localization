#!/bin/bash

# This is a shell script downloading essential files used for my semester project

cd ..

svn co https://svn.csail.mit.edu/apriltags

cd apriltags
make
./build/bin/apriltags_demo
