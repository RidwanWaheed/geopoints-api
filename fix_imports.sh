#!/bin/bash
isort app
black app
isort tests
black tests