def get_selected_columns(path):
    columns = []

    with open(path) as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_columns_to_drop():
    columns = []

    with open("./text/drop_columns.txt") as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_columns_to_scale():
    columns = []

    with open("./text/keep_columns.txt") as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_correlated_columns():
    columns = []

    with open("./text/correlated_columns.txt") as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_categorical_columns():
    columns = []

    with open("./text/categorical_columns.txt") as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_time_columns():
    columns = []

    with open("./text/time_columns.txt") as f:
        for column in f.readlines():
            columns.append(column.strip().replace("\n", ""))

    return columns


def get_target_variables():
    variables = []

    with open("./text/target_columns.txt") as f:
        for variable in f.readlines():
            variables.append(variable.strip().replace("\n", ""))

    return variables
