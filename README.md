# GenAI-SemanticSearch-FastAPI (E2E)

An implementation of Semantic Search with HuggingFace Transformer over movies dataset wrapped as FastAPI

### Services Used:

- Redis
- MongoDB & Atlas VectorSearch
- Auth0
- Docker

### Feature(s):

- Semantic Search using HuggingFace Transformer (all-MiniLM-L6-v2)
- MongoDB Atlas as Vector Store & Vector Search
- Wrapped as a FastAPI service
- Includes unit test cases

### Additional feature(s):

- Authentication with Auth0
- Rate Limiters (Sliding Window)
- Poetry Dependencies & Packaging
- CSRF Protection & Idempotecy
