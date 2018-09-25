import os
import shutil

import pytest

from autolens.autofit import link

temp_folder_path = "/tmp/linked_folder"


def delete_trees(*paths):
    for path in paths:
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)


class TestCase(object):
    def test_create_dir(self):
        assert os.path.exists(link.autolens_dir)

    def test_consistent_dir(self):
        directory = link.path_for("/a/random/directory")
        assert link.autolens_dir in directory
        assert len(directory.split("/")[-1]) == link.SUB_PATH_LENGTH
        assert directory == link.path_for("/a/random/directory")
        assert directory != link.path_for("/b/random/directory")
        assert link.path_for("/tmp/linked_file") != link.path_for("/tmp/linked_folder")

    def test_make_linked_folder(self):
        path = link.make_linked_folder(temp_folder_path)
        assert link.autolens_dir in path
        assert os.path.exists(path)
        assert os.path.exists(temp_folder_path)
        delete_trees(path, temp_folder_path)

    def test_longer_path(self):
        long_folder_path = "/tmp/folder/path"
        with pytest.raises(FileNotFoundError):
            link.make_linked_folder(long_folder_path)

    def test_clean_source(self):
        path = link.make_linked_folder(temp_folder_path)
        temp_file_path = "{}/{}".format(path, "temp")
        open(temp_file_path, "a").close()
        assert os.path.exists(temp_file_path)

        delete_trees(temp_folder_path)
        assert not os.path.exists(temp_folder_path)
        link.make_linked_folder(temp_folder_path)
        assert not os.path.exists(temp_file_path)
