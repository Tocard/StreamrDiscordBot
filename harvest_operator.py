import requests
import json

from config import load_config

cfg = load_config()


def harvest_operator_info(operator_id: str) -> dict:
        result = {}
        payload = {
            "operationName": "getOperatorById",
            "variables": {
                "operatorId": operator_id,
            },
            "query": "query getOperatorById($operatorId: ID!) {\n  operator(id: $operatorId) {\n    ...OperatorFields\n    __typename\n  }\n}\n\nfragment OperatorFields on Operator {\n  id\n  stakes(first: 1000) {\n    ...StakeFields\n    sponsorship {\n      ...SponsorshipFields\n      __typename\n    }\n    __typename\n  }\n  delegations(first: 1000) {\n    delegator {\n      id\n      __typename\n    }\n    valueDataWei\n    operatorTokenBalanceWei\n    id\n    __typename\n  }\n  slashingEvents(first: 1000) {\n    amount\n    date\n    sponsorship {\n      id\n      stream {\n        id\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  queueEntries(first: 1000) {\n    amount\n    date\n    delegator {\n      id\n      __typename\n    }\n    id\n    __typename\n  }\n  delegatorCount\n  valueWithoutEarnings\n  totalStakeInSponsorshipsWei\n  dataTokenBalanceWei\n  operatorTokenTotalSupplyWei\n  metadataJsonString\n  owner\n  nodes\n  cumulativeProfitsWei\n  cumulativeOperatorsCutWei\n  operatorsCutFraction\n  __typename\n}\n\nfragment StakeFields on Stake {\n  operator {\n    id\n    metadataJsonString\n    __typename\n  }\n  amountWei\n  earningsWei\n  lockedWei\n  joinTimestamp\n  __typename\n}\n\nfragment SponsorshipFields on Sponsorship {\n  id\n  stream {\n    id\n    metadata\n    __typename\n  }\n  metadata\n  isRunning\n  totalPayoutWeiPerSec\n  stakes(first: 1000, orderBy: amountWei, orderDirection: desc) {\n    ...StakeFields\n    __typename\n  }\n  operatorCount\n  maxOperators\n  totalStakedWei\n  remainingWei\n  projectedInsolvency\n  cumulativeSponsoring\n  minimumStakingPeriodSeconds\n  creator\n  spotAPY\n  __typename\n}",
        }
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(cfg["api_url"], headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            result = response.json()['data']['operator']
        else:
            print("Error for Operator ")
        return result


def harvest_all_operators_info() -> dict:
    result = {}
    headers = {
        "Content-Type": "application/json",
    }

    graphql_query = """
    query getAllOperators($first: Int, $skip: Int) {
      operators(first: $first, skip: $skip) {
        ...OperatorFields
        __typename
      }
    }

    fragment OperatorFields on Operator {
      id
      stakes(first: 1000) {
        ...StakeFields
        sponsorship {
          ...SponsorshipFields
          __typename
        }
        __typename
      }
      delegations(first: 1000) {
        delegator {
          id
          __typename
        }
        valueDataWei
        operatorTokenBalanceWei
        id
        __typename
      }
      slashingEvents(first: 1000) {
        amount
        date
        sponsorship {
          id
          stream {
            id
            __typename
          }
          __typename
        }
        __typename
      }
      queueEntries(first: 1000) {
        amount
        date
        delegator {
          id
          __typename
        }
        id
        __typename
      }
      delegatorCount
      valueWithoutEarnings
      totalStakeInSponsorshipsWei
      dataTokenBalanceWei
      operatorTokenTotalSupplyWei
      metadataJsonString
      owner
      nodes
      cumulativeProfitsWei
      cumulativeOperatorsCutWei
      operatorsCutFraction
      __typename
    }

    fragment StakeFields on Stake {
      operator {
        id
        metadataJsonString
        __typename
      }
      amountWei
      earningsWei
      lockedWei
      joinTimestamp
      __typename
    }

    fragment SponsorshipFields on Sponsorship {
      id
      stream {
        id
        metadata
        __typename
      }
      metadata
      isRunning
      totalPayoutWeiPerSec
      stakes(first: 1000, orderBy: amountWei, orderDirection: desc) {
        ...StakeFields
        __typename
      }
      operatorCount
      maxOperators
      totalStakedWei
      remainingWei
      projectedInsolvency
      cumulativeSponsoring
      minimumStakingPeriodSeconds
      creator
      spotAPY
      __typename
    }
    """
    graphql_request = {
        "query": graphql_query,
        "variables": {
            "first": 1000,  # Adjust as needed
            "skip": 0,
        }
    }
    response = requests.post(cfg["api_url"], headers=headers, json=graphql_request)

    if response.status_code == 200:
        result = response.json()
    else:
        print("Error for Operators ")
    return result

