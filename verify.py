import pandas as pd
from predict import load_model, predict_fraud

df = pd.read_csv("Bank_Transaction_Fraud_Detection.csv")
pipeline, threshold = load_model()

fraud_row = df[df["Is_Fraud"] == 1].iloc[0].to_dict()
legit_row = df[df["Is_Fraud"] == 0].iloc[0].to_dict()

print(predict_fraud(fraud_row, pipeline, threshold))
print(predict_fraud(legit_row, pipeline, threshold))