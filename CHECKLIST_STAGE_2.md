Stage 2: Base App Review Checklist



Reviewer Name: \[Your Name]

Role: Peer Reviewer

Repo # Reviewed:\[Partner's Repo #]

Partner Name:\[Partner Name]

Date:\[Date]

Stage Reviewed:● 2 Base App



| # | PEER REVIEW Item | PASS / FAIL |

|---|------------------|-------------|

| 1 | docker compose up starts entire app with zero manual steps | ○ PASS |

| 2 | All services have health checks with service\_healthy dependency conditions | ○ PASS |

| 3 | /health returns HTTP 200 without authentication | ○ PASS |

| 4 | UI is polished — visibly better than default LLM output | ○ PASS |

| 5 | Signup and login flows work end-to-end | ○ PASS |

| 6 | Public seed script populates app with test data successfully | ○ PASS |

| 7 | Private seed script populates app with different data, same schema | ○ PASS |

| 8 | Public and private credentials are different | ○ PASS |

| 9 | ECS task def uses localhost networking | ○ PASS |

| 10 | Dockerfile.ecs is multi-stage build with nginx | ○ PASS |

| 11 | All dependencies pinned to specific versions | ○ PASS |

| 12 | Base images are node:24-alpine and/or python:3.13-slim | ○ PASS |

| 13 | Playwright version is exactly 1.58.2 | ○ PASS |

| 14 | No dev server in production | ○ PASS |

| 15 | attack\_scope.json present and covers all required vectors | ○ PASS |

| 16 | Base test suite passes against public seed data | ○ PASS |

| 17 | Only Cursor with approved models was used | ○ PASS |



Peer Reviewer Notes: All items verified and passing.



Reviewer Signature: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Date: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

