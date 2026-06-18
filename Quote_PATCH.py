import copy
import random
from copy import deepcopy
from datetime import datetime, timezone
import requests
from config import BASE_URL_QUOTE, BASE_URL_AGREEMENT, HEADERS_QUOTE, HEADERS_AGREEMENT


# 0. KONFIGURÁCIÓ

QUOTE_ID = "1000000901"


# 1. SEGÉDFÜGGVÉNYEK ÉS TRANSZFORMÁCIÓS LOGIKA


def utc_now_formatted():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def agreement_id():
    return "KT" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def find_owner_customer(quote):
    for p in quote.get("relatedParties", []):
        if p.get("role") == "owner" and p.get("entityReferredType") == "Customer":
            return p
    return None


def convert_item_price(price):
    p = deepcopy(price)
    p["entityType"] = "ProductOfferingPrice"
    p["name"] = "recurringFees"
    if "label" not in p and "name" in price:
        p["label"] = price["name"]
    if "price" in p:
        p["price"].setdefault("percentage", 0.0)
    return p


def convert_characteristic(ch):
    c = deepcopy(ch)
    values = c.pop("characteristicValues", None)
    if values and isinstance(values, list):
        first = values[0]
        if isinstance(first, dict):
            label = first.get("label")
            if label:
                c["valueLabel"] = label
    return c


def convert_product_offering(po):
    result = deepcopy(po)
    result.pop("productSpecificationRef", None)
    result["targetScopeRef"] = {}

    characteristics = []
    for ch in result.get("characteristics", []):
        converted = convert_characteristic(ch)
        if converted.get("name") == "uniqueProductId":
            converted["value"] = ch.get("value")
        characteristics.append(converted)
    result["characteristics"] = characteristics

    prices = []
    for price in result.get("productOfferingPrices", []):
        p = deepcopy(price)
        if "price" in p:
            p["price"]["taxIncludedAmount"] = 0
            p["price"]["dutyFreeAmount"] = 0
            p["price"].setdefault("percentage", 0.0)
        p.setdefault(
            "characteristics", [{"name": "isOverriddenPrice", "value": "False"}]
        )
        prices.append(p)
    result["productOfferingPrices"] = prices
    return result


def convert_quote_item(item, grouping_id):
    agreement_item = {
        "id": item["id"],
        "entityType": item.get("entityType", "configurationItem"),
        "productOfferings": [],
        "itemPrices": [],
        "agreementItemRelationships": [{"id": grouping_id, "type": "isChildOf"}],
        "relatedEntities": [
            {"entityType": "ProductOrderItem", "relatedEntityId": item["id"]}
        ],
    }
    for po in item.get("productOfferings", []):
        agreement_item["productOfferings"].append(convert_product_offering(po))
    for price in item.get("quoteItemPrices", item.get("productOfferingPrices", [])):
        agreement_item["itemPrices"].append(convert_item_price(price))
    return agreement_item


def create_grouping_item(quote_id):
    grouping_id = str(random.randint(700000, 799999))
    grouping_item = {
        "id": grouping_id,
        "label": f"{grouping_id}_Quote ({quote_id}) alapján létrehozott",
        "entityType": "groupingItem",
        "relatedEntities": [{"entityType": "EaAov", "relatedEntityId": quote_id}],
    }
    return grouping_id, grouping_item


def build_related_parties(quote):
    result = []
    customer = None
    business_contact = None

    for p in quote.get("relatedParties", []):
        if p.get("role") == "owner" and p.get("entityReferredType") == "Customer":
            customer = p
        if (
            p.get("entityReferredType") == "ContactParty"
            and p.get("role")
            in ["companyRepresentative", "businessContact", "technicalContact"]
            and business_contact is None
        ):
            business_contact = p

    if customer:
        result.append(
            {
                "entityReferredType": "Customer",
                "id": customer["id"],
                "role": "contractOwner",
            }
        )
    if business_contact:
        result.append(
            {
                "entityReferredType": "ContactParty",
                "id": business_contact["id"],
                "role": "businessContact",
            }
        )
    return result


def build_root_related_entities(quote):
    quote_id = quote.get("id", "UNKNOWN")
    shopping_cart_id = quote.get(
        "shoppingCartId", "d47951a0-273a-46f8-8169-86953d2d2dac"
    )

    opp_id = quote.get("opportunityId", "HU-MT~0069M00000YcXKQQA3")
    opp_business_id = quote.get("opportunityBusinessId", "8046456")
    sfa_contract_id = quote.get("sfaContractId", f"HU-KT-MT~{quote_id}")
    document_id = quote.get("documentId", "69736dc79e434841de1b14a4")
    lead_id = quote.get("iccmLeadId", "8045497")

    return [
        {"entityType": "Quote", "relatedEntityId": quote_id},
        {"entityType": "ShoppingCart", "relatedEntityId": shopping_cart_id},
        {"entityType": "SourceQuote", "relatedEntityId": quote_id},
        {"entityType": "EaAov", "relatedEntityId": quote_id},
        {
            "entityType": "Opportunity",
            "relatedEntityId": opp_id,
            "relatedEntityBusinessId": opp_business_id,
            "role": "originalOpportunity",
        },
        {"entityType": "SFAContract", "relatedEntityId": sfa_contract_id},
        {
            "entityType": "Document",
            "relatedEntityId": document_id,
            "name": "Egyedi(sales) szerződés",
            "role": "frameContract",
            "characteristics": [{"name": "documentType", "value": "contract"}],
        },
        {"entityType": "IccmLead", "relatedEntityId": lead_id},
    ]


def build_agreement(quote):
    agr_id = agreement_id()
    now_str = utc_now_formatted()

    owner = find_owner_customer(quote)
    grouping_id, grouping_item = create_grouping_item(quote["id"])

    agreement = {
        "id": agr_id,
        "name": "Egyedi szolgáltatási szerződés",
        "businessId": agr_id,
        "status": "active",
        "type": "commercial",
        "subType": "salesAgreement",
        "duration": {"timePeriod": 36, "type": "month"},
        "agreementPeriod": {"startDateTime": now_str},
        "completionDate": now_str,
        "relatedParties": build_related_parties(quote),
        "agreementAuthorizations": [],
        "agreementItems": [],
    }

    if owner:
        agreement["agreementAuthorizations"].append(
            {
                "date": now_str,
                "authorizedBy": {"entityReferredType": "Customer", "id": owner["id"]},
                "signatureRepresentation": "paper",
                "state": "signed",
                "type": "authorization",
            }
        )

    agreement["agreementItems"].append(grouping_item)

    for item in quote.get("quoteItems", []):
        converted = convert_quote_item(item, grouping_id)
        agreement["agreementItems"].append(converted)

    agreement["relatedEntities"] = build_root_related_entities(quote)

    return agreement


def inject_unique_ids(data):
    counter = 1
    for item in data.get("quoteItems", []):
        for po in item.get("productOfferings", []):
            if not (po.get("group") == "tariff" and po.get("isBundle") is True):
                continue

            characteristics = po.get("characteristics", [])
            existing = next(
                (c for c in characteristics if c.get("name") == "uniqueProductId"),
                None,
            )

            if existing:
                existing["value"] = f"uniqueProductId{counter}"
            else:
                characteristics.append(
                    {
                        "entityType": "configuration",
                        "name": "uniqueProductId",
                        "label": "uniqueProductId",
                        "isCustomerVisible": False,
                        "value": f"uniqueProductId{counter}",
                        "valueType": "text",
                        "priority": 0,
                    }
                )
            counter += 1
    return data


# 2. VÉGREHAJTÁSI FOLYAMAT


def main():
    print(f"--- FOLYAMAT INDÍTÁSA - QUOTE_ID: {QUOTE_ID} ---")

    # LÉPÉS 1: GET QUOTE
    get_url = f"{BASE_URL_QUOTE}/quoteManagement/int/v1/quotes/{QUOTE_ID}"
    print(f"[1/5] GET Quote lekérése: {get_url}")
    get_resp = requests.get(get_url, headers=HEADERS_QUOTE)

    if get_resp.status_code != 200:
        print(
            f"HIBA a GET során! Status: {get_resp.status_code}, Response: {get_resp.text}"
        )
        return

    quote_data = get_resp.json()
    print("-> Sikeres lekérés.")

    print("[2/5] uniqueProductId-k generálása és beszúrása...")
    modified_quote = inject_unique_ids(copy.deepcopy(quote_data))

    patch_url = (
        f"{BASE_URL_QUOTE}/quoteManagement/int/v1/quotes/{QUOTE_ID}?fields=quoteItems"
    )
    print(f"[3/5] PATCH Quote küldése: {patch_url}")
    patch_resp = requests.patch(
        patch_url,
        headers=HEADERS_QUOTE,
        json={"quoteItems": modified_quote.get("quoteItems", [])},
    )

    if patch_resp.status_code not in [200, 201, 204]:
        print(
            f"HIBA a PATCH során! Status: {patch_resp.status_code}, Response: {patch_resp.text}"
        )
        return
    print(f"-> Sikeres PATCH. Status: {patch_resp.status_code}")

    print("[4/5] Frissített Quote újra-lekérése (GET)...")
    fresh_get_resp = requests.get(get_url, headers=HEADERS_QUOTE)
    if fresh_get_resp.status_code != 200:
        print("HIBA a frissített GET során!")
        return
    fresh_quote_data = fresh_get_resp.json()

    print("[5/5] Agreement JSON transzformáció és beküldés...")
    generated_agreement = build_agreement(fresh_quote_data)

    agreement_post_url = f"{BASE_URL_AGREEMENT}/agreements/internal/v1/agreements"
    print(f"-> POST küldése az Agreement API-nak: {agreement_post_url}")
    agreement_resp = requests.post(
        agreement_post_url, headers=HEADERS_AGREEMENT, json=generated_agreement
    )
    print(f"Agreement POST Status Code: {agreement_resp.status_code}")


if __name__ == "__main__":
    main()
