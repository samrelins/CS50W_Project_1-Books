#!/bin/bash
source /mnt/c/Users/samre/Documents/coding/cs50w/projects/project1/project1_env/bin/activate
export FLASK_APP=application.py
export DATABASE_URL=postgres://ydverjocsauovo:c0cf22a201d5ecd537447fb0976a32c8a4ae93b9d0d39e67f34a63df7b83aae7@ec2-54-247-101-205.eu-west-1.compute.amazonaws.com:5432/d9tc6m5kauc5a7
export FLASK_DEBUG=1
export GOODREADS_KEY=e7Y9uqG6dabrE3x6gMMUA
flask run
