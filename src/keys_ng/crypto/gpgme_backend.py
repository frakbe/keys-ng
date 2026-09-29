from __future__ import annotations

# The official GPGME Python bindings have historically varied by platform and
# distribution. This adapter is feature-gated until the cross-platform M2
# packaging matrix confirms a stable API/installation path.
raise ImportError("Python GPGME adapter is not enabled in this build; use the safe gpg process backend")
