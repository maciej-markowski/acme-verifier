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


### sample verify

```bash
kubectl port-forward svc/access-verifier-service 8080:8080
```

```bash
curl --header "Content-Type: text/plain" --request POST --data 'GET / HTTP/1.1
Host: 127.0.0.1:3000
User-Agent: curl/7.85.0
Accept: */*
X-Forwarded-For: 3.4.15.169 202.54.22.11
Something-Else: dddd' http://localhost:8080 -v

Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying ::1:8080...
* TCP_NODELAY set
* Connected to localhost (::1) port 8080 (#0)
> POST / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.65.0
> Accept: */*
> Content-Type: text/plain
> Content-Length: 133
>
* upload completely sent off: 133 out of 133 bytes
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: BaseHTTP/0.6 Python/3.12.8
< Date: Mon, 16 Dec 2024 15:58:08 GMT
< Content-type: text/plain
<
* Closing connection 0
OK            
```

```bash
curl --header "Content-Type: text/plain" --request POST --data 'GET / HTTP/1.1
Host: 127.0.0.1:3000
User-Agent: curl/7.85.0
Accept: */*
X-Forwarded-For: 3.4.15.180 202.54.22.11
Something-Else: dddd' http://localhost:8080 -v

Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying ::1:8080...
* TCP_NODELAY set
* Connected to localhost (::1) port 8080 (#0)
> POST / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.65.0
> Accept: */*
> Content-Type: text/plain
> Content-Length: 133
>
* upload completely sent off: 133 out of 133 bytes
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 401 Unauthorized
< Server: BaseHTTP/0.6 Python/3.12.8
< Date: Mon, 16 Dec 2024 16:13:53 GMT
< Content-type: text/plain
<
* Closing connection 0
Unauthorized                                                                                                                                                                                                   ✔


```

```bash
curl --header "x-forwarded-for: 192.168.3.11" localhost:8080 -v

*   Trying ::1:8080...
* TCP_NODELAY set
* Connected to localhost (::1) port 8080 (#0)
> GET / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.65.0
> Accept: */*
> x-forwarded-for: 192.168.3.11
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 401 Unauthorized
< Server: BaseHTTP/0.6 Python/3.12.8
< Date: Mon, 16 Dec 2024 15:57:40 GMT
< Content-type: text/plain
<
* Closing connection 0
Unauthorized   
```

```bash
curl --header "x-forwarded-for: 3.4.15.169" localhost:8080 -v

*   Trying ::1:8080...
* TCP_NODELAY set
* Connected to localhost (::1) port 8080 (#0)
> GET / HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.65.0
> Accept: */*
> x-forwarded-for: 3.4.15.169
>
* Mark bundle as not supporting multiuse
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Server: BaseHTTP/0.6 Python/3.12.8
< Date: Mon, 16 Dec 2024 15:57:57 GMT
< Content-type: text/plain
<
* Closing connection 0
OK        
```