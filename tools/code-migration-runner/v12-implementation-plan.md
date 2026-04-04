# V12 Implementation Plan

## Step 1

Add OpenAI support to model_backend.py

## Step 2

Add auto-openai mode to migration_execute.py

## Step 3

Limit to analyzer + planner only

## Step 4

Test failure:

- missing OPENAI_API_KEY

## Step 5

Test success:

- analyzer-output.md created
- planner-output.md created

## Rule

Do not touch coder/apply/reviewer
