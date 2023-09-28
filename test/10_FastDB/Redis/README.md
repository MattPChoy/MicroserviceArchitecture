# Redis Test Setup

## Test Setup
1. Run Redis 
    ```bash
   docker run --name some-redis -d redis redis-server --save 60 1 --loglevel warning
   ```
