# DNS to DoT Proxy

## Overview

Written using Python language proxy forwarding DNS queries over TLS for secure, private communications. It listens on port 53, directing queries to Cloudflare's DoT endpoint (`1.1.1.1:853`)

## Security

Key concerns include the need for root access for binding 53 port, ensuring TLS security, managing query log privacy, and protecting against DoS attacks.

## Integration

For microservices architectures:
- **Containerized** with Docker for easy deployment.
- **Kubernetes** deployment can easily use docker image builded using Dockerfile

## Enhancements

Proposed improvements: include DNS query caching, load balancing, integration with monitoring tools like Prometheus, and enhanced security measures (IP filtering, rate limiting).

## Setup

### Prerequisites
- Docker
- docker-compose

### Instructions

1. Build: `docker-compose build`
2. Deploy: `docker-compose up -d`
3. This stack mapping ```5553``` port to ```53``` port inside container for testig purposes.

### Testing

Configure DNS client to use ```localhost``` as DNS server
example: ```dig @localhost -p 5553 +tcp wwww.com```

you should see something like:
