__version__ = "1.0.0"

BANNER = r"""
 _   _ _ __  _ __ ___   __ _ _ __ (_)___ 
| | | | '_ \| '_ ` _ \ / _` | '_ \| / __|
| |_| | | | | | | | | | (_| | |_) | \__ \
 \__,_|_| |_|_| |_| |_|\__,_| .__// |___/
                            |_| |__/     
      github: @atiilla
"""

SOURCE_PATH_PREFIXES = [
    "turbopack:///[project]/",
    "turbopack:///[turbopack]/",
    "webpack:///",
    "webpack:///_N_E/",
    "webpack:///./",
    "vite:///",
    "rollup:///",
]

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

DEFAULT_CONCURRENCY = 10
DEFAULT_OUTPUT_DIR = "./recovered-source"
DEFAULT_TIMEOUT = 15
SOURCEMAP_TIMEOUT = 30

PROBE_PATHS = [
    # Auth
    "/login",
    "/signin",
    "/signup",
    "/register",
    "/forgot-password",
    "/reset-password",
    "/verify",
    "/oauth/callback",
    # Main app
    "/dashboard",
    "/app",
    "/home",
    "/landing",
    # Account
    "/profile",
    "/settings",
    "/account",
    "/preferences",
    # Content
    "/search",
    "/explore",
    "/feed",
    "/notifications",
    "/messages",
    "/chat",
    # Commerce
    "/pricing",
    "/checkout",
    "/cart",
    "/orders",
    "/billing",
    # Admin
    "/admin",
    "/admin/dashboard",
    "/manage",
    # Common pages
    "/about",
    "/contact",
    "/help",
    "/faq",
    "/docs",
    "/terms",
    "/privacy",
    # API docs
    "/api-docs",
    "/swagger",
    "/graphql",
    # Errors
    "/404",
    "/500",
]
