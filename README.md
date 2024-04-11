# DNS to DoT Proxy

## Overview

Written using Python language proxy forwarding DNS queries over TLS for secure
- private communications.

It listens on port 53, directing queries to Cloudflare's DoT endpoint (`1.1.1.1:853`)

## Security concerns

Key concerns include:
 - the need for root access for binding **53** port
 - ensuring TLS security
 - managing query log privacy
 - protecting against DoS attacks.

## Integration for microservices architectures

- **Containerized** with Docker for easy deployment.
- **Kubernetes** deployment can easily use docker image builded using Dockerfile

## Proposed improvements

- include DNS query caching
- integration with monitoring tools like Prometheus
- enhanced security measures (IP filtering, rate limiting).

## Setup

### Prerequisites
- Docker
- docker-compose

### Instructions

1. Build and Deploy: `docker-compose up --build`
2. This stack mapping host port ```5553``` to container port ```53``` for testig purposes, because for binding ```53``` port you need root privileges

### Testing

Configure DNS client to use ```localhost``` as DNS server and use **TCP** queries

**Example**:
```
dig @localhost -p 5553 +tcp wwww.com
dig @localhost -p 5553 +tcp google.com
dig @localhost -p 5553 +tcp n26.com
```

you should see something like:
```
❯ dig @localhost -p 5553 +tcp wwww.com

; <<>> DiG 9.10.6 <<>> @localhost -p 5553 +tcp wwww.com
; (2 servers found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 22876
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 1232
; PAD: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 ("...........................................................................................................................................................................................................................................................................................................................................................................................................................")
;; QUESTION SECTION:
;wwww.com.			IN	A

;; ANSWER SECTION:
wwww.com.		26908	IN	A	31.31.196.223

;; Query time: 149 msec
;; SERVER: ::1#5553(::1)
;; WHEN: Thu Apr 11 11:49:07 EEST 2024
;; MSG SIZE  rcvd: 468
```

And inside docker logs you will see:
```
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Listening for DNS on ('', 53)
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Handling client connection
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Parsed domain name: www.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Received DNS query for www.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Response sent back to client for www.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Handling client connection
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Parsed domain name: google.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Received DNS query for google.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Response sent back to client for google.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Handling client connection
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Parsed domain name: n26.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Received DNS query for n26.com
dns-proxy-dns-proxy-1  | INFO:DNSProxy:Response sent back to client for n26.com
```
