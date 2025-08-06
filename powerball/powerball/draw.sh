#!/bin/bash
sqlite3 powerball_draws.db << EOF
.headers on
.mode box
EOF
