# acme-verifier


## task

ClientDataManager works in K8s Azure. 
It's client is strictly an app running in AWS Europe West region.
Create AccessVerifier to limit access only to IPs from that AWS region:
    - ClientDatamanager sends full http header of its request to AccessVerifier as text/plain
    - AccessVerifier returns 200 OK or 401 Unauthorized 
    - AccessVerifier refreshes AWS IP ranges daily


## solution

Sample deployment + service exposing it internally.

Deployment creates a pod with two containers:
    - sidecar `range-getter` that handles getting AWS IP ranges for given region
    - app container `verifier` that runs simple http server, listening for POST requests. It extracts IP address from X-Forwarded-For and checks if it matches the whitelist.

Client can send GET request with forwarded headers, or POST with plaintext headers as data.
