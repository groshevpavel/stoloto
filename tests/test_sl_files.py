import contextlib

from stoloto import sl_files


@contextlib.contextmanager
def make_fake_files(dir, filename: str, filext: str, textinfile: str, num_files: int = 3):
    res = []
    for n in range(num_files):
        f = dir.join(f'{filename}{n}.{filext}')
        f.write(textinfile)
        res.append(f)
    yield res

    res[0].dirpath().dirpath().remove()
    print(f'{res[0].dirpath().dirpath()} wiped')


def make_fake_text_files(dir, filename, textinfile, num_files=3):
    return make_fake_files(
        dir,
        filename,
        'txt',
        textinfile,
        num_files=num_files,
    )


def test_get_archive_filenames(tmpdir):
    with make_fake_text_files(tmpdir, 'page', 'fake file', num_files=3) as files:
        res = sl_files.get_archive_filenames(folder=tmpdir)
        res = list(res)

        assert res == files, res


# def