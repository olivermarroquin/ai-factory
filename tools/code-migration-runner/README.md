# Code Migration Runner

## Purpose

This tool automates the setup and packaging of a code migration step.

It is the first automation layer for the code-migration workflow.

## What It Does

Given:

- venture
- step number
- source file
- target file
- goal

It should:

- create migration log artifacts
- generate prompt files
- prefill planner, reviewer, and summary files
- package the migration step in a consistent format

## What It Does Not Do

It does not:

- edit source code automatically
- auto-approve changes
- auto-merge changes
- replace human review

## Role in System

This is the bridge between:

- manual structured workflow
- future multi-agent automation
