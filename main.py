from pathlib import Path
import pandas as pd
from model.train_model import run_regression_model, run_classification_model, save_best_regression_model, save_best_classification_model

PRODUCTS = ['consumer_loans', 'credit_cards']
BUCKETS = [2,3,4]
ACTIONS = ['ptp', 'rpc']

model_path = Path("./models")
model_path.mkdir(parents=True, exist_ok=True)

features_path = Path("./features")
features_path.mkdir(parents=True, exist_ok=True)

path = Path(
    "C:/Users/j.lloyd/Desktop/Projects/reporting_ng/komplett_data/code/reportingng-model-training/data"
)


def train_classification_models():
    for product in PRODUCTS:
        for bucket in BUCKETS:
            for action in ACTIONS:

                data = pd.read_csv(path / f"{product}_{bucket}_{action}.csv")

                if bucket == 4:
                    df = pd.read_csv(path / f"{product}_3_{action}.csv")
                    df = df[df.DF_last_action_was_ptp > 0]

                    data = pd.concat([data, df], axis=0)

                names = []
                stats = []

                print(f"Running code for {product}_{bucket}_{action}")
                try:
                    name, stat = run_classification_model(data, 'logistic_regression', product, bucket, action)

                    names += name
                    stats += stat

                    save_best_classification_model(names, stats, product, bucket, action)

                except ValueError:
                    print(f"Failed to run code for {product}_{bucket}_{action}! Not enough events to predict!")
                print("")


def train_regression_model():

    data = pd.read_csv(path / f"number_of_actions.csv")

    names = []
    stats = []

    print(f"Running code for number_of_actions")
    name, stat = run_regression_model(data, 'linear_regression')

    names += name
    stats += stat

    save_best_regression_model(names, stats)


if __name__ == "__main__":
    train_classification_models()
    train_regression_model()
