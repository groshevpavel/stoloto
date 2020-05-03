from pathlib import Path

import pickle
import csv


def get_archive_filenames(folder, in_filename: [str, list], func=None):
    for file in Path(folder).iterdir():
        if not isinstance(in_filename, str):
            if not any([i in str(file) for i in in_filename]):
                continue
        elif in_filename not in str(file):
            continue

        if func and callable(func):
            yield func(file)
        else:
            yield file


def get_dir(filename) -> Path:
    return Path(filename).parent


def check_exist(filename):
    if isinstance(filename, str):
        filename = Path(filename)
    return filename.exists()


def check_and_create_dirs(filename):
    if not check_exist(filename):
        filename.mkdir(parents=True, exist_ok=True)


def save_pickle(pickle_filename: Path, data):
    with pickle_filename.open('wb') as pickle_file:
        pickle.dump(data, pickle_file)


def load_pickle(pickle_filename):
    try:
        with open(pickle_filename, 'rb') as pickle_file:
            data = pickle.load(pickle_file)
            print(f'Loaded "{pickle_filename}" with {len(data)} records')
            return data
    except FileNotFoundError:
        print(f'{pickle_filename} was not found, returning empty list')
        return []


def save_csv(csv_filename, data, writemode="w", header=[], delimiter=';'):
    with open(csv_filename, writemode, newline='') as csvfile:
        if isinstance(data[0], dict):
            writer = csv.DictWriter(csvfile, data[0].keys(), delimiter=delimiter, dialect="excel")
            writer.writeheader()
            try:
                writer.writerows(data)
            except ValueError:
                print(f'{csv_filename}: skipped {data}')
        else:
            writer = csv.writer(csvfile, delimiter=delimiter, dialect="excel")

            if isinstance(data, tuple):
                data = [data]

            for row in data:
                row = tuple(
                    ['"%s"' % r if isinstance(r, str) and not (r.startswith('"') and r.endswith('"')) else r for r in
                     row])
                writer.writerow(row)

    if len(data) > 1:
        print(f'Saved {len(data)} records into "{csv_filename}"')
