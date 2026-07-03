from src.ddi.drug_search import (
    search_drugs,
    resolve_alias,
    drug_exists
)

print("\nAlias Tests")
print(resolve_alias("aspirin"))
print(resolve_alias("crocin"))
print(resolve_alias("tylenol"))

print("\nSearch Tests")
print(search_drugs("aba"))
print(search_drugs("met"))

print("\nExists Tests")
print(drug_exists("aspirin"))
print(drug_exists("abacavir"))
print(drug_exists("randomdrug"))