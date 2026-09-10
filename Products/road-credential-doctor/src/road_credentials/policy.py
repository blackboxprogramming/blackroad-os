RISK_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def risk_allows(credential_risk: str, approved_through: str) -> bool:
    return RISK_RANK.get(credential_risk, 99) <= RISK_RANK.get(approved_through, -1)
