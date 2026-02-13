# Development Process

This project was implemented step by step to simulate a simple GPU job management service.

## Step 1 — Basic FastAPI setup

First, we created a minimal FastAPI server and verified that endpoints were reachable from Postman.

## Step 2 — Database models

We added database models for User and Job and connected SQLite to store persistent data.

## Step 3 — Authentication

User registration and login were implemented using JWT tokens so each request could be authenticated.

## Step 4 — Roles (User / Admin)

We introduced role-based access control:

* Users can submit jobs
* Admins can approve jobs

## Step 5 — Job workflow

We implemented the job lifecycle:
PENDING → APPROVED → RUNNING → COMPLETED

The system prevents invalid transitions (for example approving a completed job).

## Step 6 — Background simulator

A background worker was added to simulate job execution after approval.

## Step 7 — Validation & schemas

Input validation was added using schemas to ensure correct request data.

## Step 8 — Testing and improvements

We tested endpoints using Postman and fixed workflow edge cases such as duplicate users and invalid approvals.

---

This project focuses on understanding backend workflow and resource management rather than real GPU execution.
