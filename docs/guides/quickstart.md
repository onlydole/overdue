---
title: Quick Start
category: guides
---

# Quick Start

Get up and running with Overdue in under five minutes.

## 1. Install

```bash
git clone https://github.com/onlydole/overdue.git
cd overdue
pip install -e ".[dev]"
```

## 2. Start the server

```bash
uvicorn src.main:app --reload
```

The API is now running at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive API documentation.

## 3. Create a shelf

```bash
curl -X POST http://localhost:8000/api/shelves/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Cloud Native", "description": "All things Kubernetes and beyond"}'
```

## 4. Shelve a volume

```bash
curl -X POST http://localhost:8000/api/volumes/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Container Orchestration 101",
    "content": "Kubernetes manages containerized workloads...",
    "shelf_id": 1,
    "bookmarks": ["kubernetes", "containers"]
  }'
```

## 5. Check the reading room

```bash
curl http://localhost:8000/api/reading-room/health
```

You should see the library's mood and health stats.

## 6. Review a volume

As time passes, volumes accumulate dust (their Dewey Score decays). Keep them fresh by reviewing:

```bash
curl -X POST http://localhost:8000/api/volumes/1/review
```

## Next steps

- [Configuration](configuration.md) -- Customize your library settings
- [API Endpoints](../api/endpoints.md) -- Full endpoint reference
- [Architecture](../architecture/overview.md) -- How it all fits together
