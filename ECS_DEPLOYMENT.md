# ECS Deployment Guide

## Overview
This document describes how to deploy the DigiMart application to AWS ECS.

## Prerequisites
- AWS CLI configured (`aws configure`)
- Docker installed
- ECR Repository created

## Build and Push
Run the build script to build images and push to ECR:
```bash
chmod +x build-and-push-ecs.sh
./build-and-push-ecs.sh