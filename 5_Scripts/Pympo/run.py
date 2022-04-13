#!/usr/bin/env python
#############################################################
# File: run.py
# Function: Script which calls the main function
# Author: Bruno Luna
# Date: 10/04/11
# Modifications Date:
# 
#
#
#
#
############################################################
import sys,os

print "    _____                                                     "
print"  __|__   |__  ______  ____    ______  ____  ____   _  ______  "
print" |     \     ||   ___||    |  |   ___||    ||    \ | ||   ___| "
print" |      \    ||   ___||    |_ |   ___||    ||     \| ||   ___| "
print" |______/  __||______||______||___|   |____||__/\____||______| "
print"    |_____| "
print" "
if (len(sys.argv) == 2):

        os.system('./Src/main.py ' + sys.argv[1])
else:
        print "Error(0):"
        print "Correct program usage: ./run.py 'caseName' "
        print " "
        sys.exit(1)
############################################################
