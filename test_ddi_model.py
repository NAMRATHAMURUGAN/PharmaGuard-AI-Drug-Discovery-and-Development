from src.ddi.ddi_predictor import predict_ddi

pairs = [

    ("Abacavir", "Omeprazole"),

    ("Metformin", "Ibuprofen"),

    ("Rosuvastatin", "Digoxin")

]

for a, b in pairs:

    result = predict_ddi(a, b)

    print("\n")
    print("=" * 50)

    print(a, "+", b)

    print(result)