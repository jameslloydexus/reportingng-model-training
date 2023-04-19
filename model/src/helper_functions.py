import copy

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
import pickle

from model.src.get_columns_functions import (
    get_target_variables,
    get_columns_to_drop,
    get_categorical_columns,
    get_time_columns,
    get_correlated_columns,
    get_columns_to_scale,
    get_selected_columns,
)


def save_selected_columns(read_path, save_path):
    selected_features = get_selected_columns(read_path)

    with open(save_path, "w") as f:
        f.write(
            "case_id"
        )
        for feature in selected_features:
            if feature == '':
                continue
            f.write("\n" + feature)


def drop_columns(data):
    columns = get_columns_to_drop()
    data.drop(columns, axis=1, inplace=True)

    return data


def drop_other_target_variables(data, target):
    variables_to_drop = list(set(get_target_variables()) - {target})

    return data.drop(variables_to_drop, axis=1)


def one_hot_encode(data):
    categorical_columns = get_categorical_columns()
    data = pd.get_dummies(data, columns=categorical_columns, drop_first=True)

    return data


def do_data_preparation(original_data, target, code):

    data = copy.deepcopy(original_data)

    data = drop_columns(data)

    data = drop_other_target_variables(data, target)
    data = data[~data[target].isna()]
    data.fillna(0, inplace=True)

    data.set_index("case_id", inplace=True)

    scaler = pickle.load(open(f"./scalers/{code}.pkl", "rb"))
    scale_columns = get_columns_to_scale()

    data[scale_columns] = scaler.transform(data[scale_columns])

    return data


def do_train_test_split(
    original_data,
    target,
    code,
    proportion=0.3,
    drop_time=False,
    drop_correlated=True
):
    data = do_data_preparation(original_data, target, code)

    X_train, X_test, y_train, y_test = train_test_split(
        data.drop(target, axis=1), data[target], test_size=proportion, random_state=42
    )

    if drop_time:
        X_train = X_train.drop(get_time_columns(), axis=1)
        X_test = X_test.drop(get_time_columns(), axis=1)

    if drop_correlated:
        X_train = X_train.drop(get_correlated_columns(), axis=1)
        X_test = X_test.drop(get_correlated_columns(), axis=1)

    return X_train, X_test, y_train, y_test


def eval_metrics(actual, pred):
    acc = accuracy_score(actual, pred)
    prec = precision_score(actual, pred)
    rec = recall_score(actual, pred)
    f1 = f1_score(actual, pred)
    auc = roc_auc_score(actual, pred)

    return acc, prec, rec, f1, auc


def pickle_model(model, model_name="model"):
    pickle.dump(model, open(f"../models/{model_name}.pkl", "wb"))


def get_highly_correlated_features(data):
    correlation_dictionary = {}
    correlations = data.corr()

    for col in correlations.columns.values:
        corred_cols = correlations[col][correlations[col] > 0.8].index.values
        corred_cols = list(set(corred_cols) - {col})

        if len(corred_cols) > 0:
            correlation_dictionary[col] = corred_cols

    return correlation_dictionary
