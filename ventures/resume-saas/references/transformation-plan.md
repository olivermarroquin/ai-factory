# Resume SaaS Transformation Plan

## Goal

Convert the existing resume-factory system into a web-based application without throwing away proven logic.

## What Should Be Reused

- resume generation logic
- prompt construction logic
- document generation logic
- workflow knowledge
- validation and structured processing patterns

## What Must Change

- terminal inputs must become web form inputs or uploads
- bash-first flows must be wrapped or replaced by backend/API flows
- local file-driven steps must be adapted for app-based request handling
- one-user assumptions must be identified and isolated

## What Must Be Avoided

- rewriting everything from scratch without reason
- copying old structure blindly into a web app
- bringing product-specific CLI clutter directly into the new app
- introducing multi-user complexity too early

## MVP Transformation Path

1. identify core reusable logic in resume-factory
2. isolate logic from shell-specific execution
3. define the minimum backend flow
4. define the minimum UI flow
5. create the new app repo
6. rebuild the workflow in web form
7. test end-to-end with one simple use case first
