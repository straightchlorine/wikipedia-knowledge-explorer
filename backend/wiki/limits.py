"""Single source of truth for the slowapi rate limiter.

Constructing `Limiter(...)` more than once produces independent buckets:
decorators bound to one instance and the FastAPI `state.limiter`/handler bound
to another would silently disagree, leading to bypass or double-counting.
Import `limiter` from this module everywhere it's needed.

Keying: `get_ipaddr` honors X-Forwarded-For so each real client gets its own
bucket behind an ingress/proxy. This REQUIRES uvicorn to be invoked with
`--proxy-headers --forwarded-allow-ips=<trusted-cidr>` (e.g. the ingress
controller's pod CIDR). Without that, X-Forwarded-For is ignored and we
fall back to the proxy's IP — all clients share one bucket. Infra must
configure uvicorn accordingly in the deployment.
"""

from slowapi import Limiter
from slowapi.util import get_ipaddr

limiter = Limiter(key_func=get_ipaddr)
