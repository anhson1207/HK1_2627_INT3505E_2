
#!/bin/bash
set -e

newman run postman/books-api.postman_collection.json \
  -e postman/local.postman_environment.json \
  --env-var base_url=http://127.0.0.1:5001 \
  -r cli,junit \
  --reporter-junit-export junit.xml
