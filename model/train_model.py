from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.feature_selection import RFECV
from sklearn.metrics import f1_score
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from sklearn.metrics import mean_squared_error
from pathlib import Path
import pandas as pd
import pickle

import warnings

warnings.filterwarnings("ignore")

from model.src.helper_functions import (
    do_train_test_split,
    save_selected_columns,
)

DATA_FILTERS = {
    'drop_correlated': {"drop_time": False, "drop_correlated": True},
    'drop_time': {"drop_time": True, "drop_correlated": True},
}

model_path = Path("./models")
model_path.mkdir(parents=True, exist_ok=True)

features_path = Path("./features")
features_path.mkdir(parents=True, exist_ok=True)


def logistic_regression_pipeline(model, X, y):
    scores = {}
    rfecv = RFECV(
        estimator=LogisticRegression(max_iter=5000),
        step=1,
        cv=5,
        scoring="f1"
    )
    rfecv.fit(X, y)
    scores [rfecv.score(X, y)] = list(rfecv.get_feature_names_out())

    bfs = SFS(
        LogisticRegression(max_iter=5000),
        k_features=(1, X.shape[1]),
        forward=False,
        verbose=0,
        scoring='roc_auc',
        cv=5
    )
    bfs.fit(X, y)
    scores[bfs.k_score_] = list(bfs.k_feature_names_)

    ffs = SFS(
        LogisticRegression(max_iter=5000),
        k_features=(1, X.shape[1]),
        forward=True,
        verbose=0,
        scoring='roc_auc',
        cv=5
    )
    ffs.fit(X, y)
    scores[ffs.k_score_] = list(ffs.k_feature_names_)

    selected_features = scores[max(scores.keys())]
    model.fit(X[selected_features], y)

    return model, selected_features


def linear_regression_pipeline(model, X, y):
    scores = {}
    rfecv = RFECV(
        estimator=LinearRegression(),
        step=1,
        cv=5,
    )
    rfecv.fit(X, y)
    scores [rfecv.score(X, y)] = list(rfecv.get_feature_names_out())

    bfs = SFS(
        LinearRegression(),
        k_features=(1, X.shape[1]),
        forward=False,
        verbose=0,
        cv=5
    )
    bfs.fit(X, y)
    scores[bfs.k_score_] = list(bfs.k_feature_names_)

    ffs = SFS(
        LinearRegression(),
        k_features=(1, X.shape[1]),
        forward=True,
        verbose=0,
        cv=5
    )
    ffs.fit(X, y)
    scores[ffs.k_score_] = list(ffs.k_feature_names_)

    selected_features = scores[max(scores.keys())]
    model.fit(X[selected_features], y)

    return model, selected_features


def run_classification_model(data, model_name, product, bucket, action):

    names = []
    stats = []

    for key in DATA_FILTERS.keys():

        X, X_, y, y_ = do_train_test_split(
            data,
            "DF_last_action_was_" + action,
            drop_time=DATA_FILTERS[key]["drop_time"],
            drop_correlated=DATA_FILTERS[key]["drop_correlated"],
            code = f"{product}_{bucket}_{action}"
        )

        model = LogisticRegression(max_iter=10000)
        run_name = f"{model_name}_{product}_{bucket}_{action}_{key}"

        model, selected_features = logistic_regression_pipeline(model, X, y)
        predicted_qualities = model.predict(X_[selected_features].fillna(0))

        f1 = f1_score(y_, predicted_qualities)

        pickle.dump(model, open(model_path / f"{run_name}.pkl", "wb"))

        with open(features_path / f"{run_name}.txt", "w") as f:
            for feature in selected_features:
                f.write("\n" + feature)

        names.append(run_name)
        stats.append(f1)

    return names, stats


def run_regression_model(data, model_name):

    names = []
    stats = []

    for key in DATA_FILTERS.keys():

        X, X_, y, y_ = do_train_test_split(
            data,
            "DF_average_actions_required_per_case",
            drop_time=DATA_FILTERS[key]["drop_time"],
            drop_correlated=DATA_FILTERS[key]["drop_correlated"],
            code='number_of_actions'
        )

        model = LinearRegression()
        run_name = f"{model_name}_{key}"

        model, selected_features = linear_regression_pipeline(model, X, y)
        predicted_qualities = model.predict(X_[selected_features].fillna(0))

        mse = mean_squared_error(y_, predicted_qualities)

        pickle.dump(model, open(model_path / f"{run_name}.pkl", "wb"))

        with open(features_path / f"{run_name}.txt", "w") as f:
            for feature in selected_features:
                f.write("\n" + feature)

        names.append(run_name)
        stats.append(mse)

    return names, stats


def save_best_classification_model(names, stats, product, bucket, action):

    results = pd.DataFrame({"names": names, "stats": stats}).sort_values(
        "stats", ascending=False
    )
    model_name = results.names.values[0]
    print (f"\n{model_name} was chosen.")
    best_model = pickle.load(open(model_path / f"{model_name}.pkl", "rb"))

    pickle.dump(
        best_model,
        open(
            f"C:/Users/j.lloyd/Desktop/Projects/reporting_ng/komplett_data/code/reportingng-prediction-rest-api/models/{product}_{bucket}_{action}.pkl",
            "wb",
        ),
    )

    save_selected_columns(
        features_path / f"{model_name}.txt",
        f"C:/Users/j.lloyd/Desktop/Projects/reporting_ng/komplett_data/code/reportingng-batch-job/text_files/{product}_{bucket}_{action}.txt",
    )


def save_best_regression_model(names, stats):

    results = pd.DataFrame({"names": names, "stats": stats}).sort_values(
        "stats", ascending=True
    )
    model_name = results.names.values[0]
    print (f"\n{model_name} was chosen.")
    best_model = pickle.load(open(model_path / f"{model_name}.pkl", "rb"))

    pickle.dump(
        best_model,
        open(
            f"C:/Users/j.lloyd/Desktop/Projects/reporting_ng/komplett_data/code/reportingng-prediction-rest-api/models/number_of_actions.pkl",
            "wb",
        ),
    )

    save_selected_columns(
        features_path / f"{model_name}.txt",
        f"C:/Users/j.lloyd/Desktop/Projects/reporting_ng/komplett_data/code/reportingng-batch-job/text_files/number_of_actions.txt",
    )
