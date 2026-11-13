# Infrastructure

Initial architecture: Next.js frontend + independently deployed Python FastAPI backend + **dedicated Supabase Cloud PostgreSQL project**. Do not introduce local production Postgres. Backend credentials belong in a secret manager. Production requirements include TLS, database migrations, backups and recovery, metrics, agent tool traces, managed queues/workers, approved gateway/supplier adapters and a private media bucket. The attached SQL migration is source-controlled but has NOT been applied to any cloud project.
