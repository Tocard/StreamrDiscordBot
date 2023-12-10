from config import load_config
import humanize

cfg = load_config()

GWEI_CONST = cfg["GWEI_CONST"]


def get_slashed_amount(slash_events: list) -> float:
    amount = 0
    for event in slash_events:
        amount = amount + float(event['amount'])
    return amount * GWEI_CONST


def get_delegator_address(delegations: list) -> list:
    delegator = []
    for delegation in delegations:
        delegator.append(delegation["delegator"]["id"])
    return delegator


def normalize(nbr_to_normalize: float) -> str:
    return humanize.intcomma(nbr_to_normalize, 2)


def convert_json_type(operator: dict) -> dict:
    print(operator)
    operator["_cumulativeProfitsWei"] = float(operator["cumulativeProfitsWei"]) * GWEI_CONST
    operator["_operatorsCutFraction"] = float(operator["operatorsCutFraction"]) * GWEI_CONST
    operator["_dataTokenBalanceWei"] = float(operator["dataTokenBalanceWei"]) * GWEI_CONST
    operator["_totalStakeInSponsorshipsWei"] = float(operator["totalStakeInSponsorshipsWei"]) * GWEI_CONST
    operator["_valueWithoutEarnings"] = float(operator["valueWithoutEarnings"]) * GWEI_CONST
    return operator

