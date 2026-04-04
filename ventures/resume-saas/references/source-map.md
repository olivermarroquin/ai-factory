# Resume SaaS Source Map

## Purpose

This file maps the current source system to the future target system.

## Source System

Current source repo:

- ~/workspace/repos/resume-factory

Current source type:

- local CLI-based system
- bash + python driven
- built for one user (me)

## Target System

Future target repo:

- ~/workspace/repos/resume-saas

Target type:

- web application
- UI + backend/API
- usable by non-CLI users
- designed for future multi-user expansion

## Main Reuse Goal

Reuse as much proven logic from resume-factory as possible while replacing the local CLI flow with a web-based flow.

## Main Shift

Current:
user → terminal commands → local scripts → generated resume

Target:
user → web UI → backend/API → generation pipeline → downloadable result

## Related Locations

Planning docs:

- ~/workspace/second-brain/03_ventures/resume-saas

Execution wrapper:

- ~/workspace/ai-factory/ventures/resume-saas

Reusable standards/templates:

- ~/workspace/repos/ai-agency-core
