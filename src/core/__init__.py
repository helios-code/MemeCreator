"""
DEPRECATED: This module is deprecated and will be removed in a future version.
Please use the new MVC structure instead:
- models/ for data models
- views/ for presentation logic
- controllers/ for business logic
"""

import warnings

warnings.warn(
    "The core module is deprecated and will be removed in a future version. "
    "Please use the new MVC structure instead.",
    DeprecationWarning,
    stacklevel=2
)
