# train_model.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from joblib import dump

df = pd.read_csv("synth.csv")

# features / target
X = df.drop(columns=["effective_minutes"])
y = df["effective_minutes"]

# categorical / numeric
cat_cols = ["subject","subj_difficulty"]
num_cols = ["age","grade","sleep_hours","days_remaining","family_event","slot_hour","is_weekend","attention_span","chapters_remaining","urgency"]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
])

model = Pipeline([
    ("prep", preprocessor),
    ("rf", RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1))
])

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.15, random_state=42)
model.fit(X_train, y_train)

# quick eval
from sklearn.metrics import mean_absolute_error, mean_squared_error
pred = model.predict(X_val)
from math import sqrt
print("MAE:", mean_absolute_error(y_val, pred))
mse = mean_squared_error(y_val, pred)   # returns MSE
print("RMSE:", sqrt(mse))


# save
dump(model, "model.joblib")
print("Saved model.joblib")
