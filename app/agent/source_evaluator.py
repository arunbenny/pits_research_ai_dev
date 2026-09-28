from urllib.parse import urlparse


TRUSTED_PUBLICATIONS = {
    "autocarindia.com",
    "bikewale.com",
    "zigwheels.com",
}


def get_domain(url: str) -> str:
    """Extract a clean domain from a URL."""

    domain = urlparse(url).netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def matches_domain(
    domain: str,
    known_domain: str,
) -> bool:
    """
    Match root domain and subdomains.

    Example:
    python.org -> True
    docs.python.org -> True

    bajajauto.com -> True
    cdn.bajajauto.com -> True
    """

    return (
        domain == known_domain
        or domain.endswith("." + known_domain)
    )


def evaluate_source(
    evidence: dict,
    official_domain: str | None = None,
) -> dict:

    url = evidence.get("link", "")
    domain = get_domain(url)

    is_official = False

    if official_domain:
        is_official = matches_domain(
            domain,
            official_domain,
        )

    is_trusted_publication = any(
        matches_domain(
            domain,
            trusted_domain,
        )
        for trusted_domain in TRUSTED_PUBLICATIONS
    )

    if is_official:
        source_type = "official"
        confidence = "high"

    elif is_trusted_publication:
        source_type = "established_publication"
        confidence = "medium"

    else:
        source_type = "other"
        confidence = "low"

    return {
        "title": evidence.get("title", ""),
        "url": url,
        "domain": domain,
        "snippet": evidence.get("snippet", ""),
        "source_type": source_type,
        "confidence": confidence,
    }


def evaluate_sources(
    evidence_list: list,
    official_domain: str | None = None,
) -> list:

    return [
        evaluate_source(
            evidence,
            official_domain,
        )
        for evidence in evidence_list
    ]