
worlds = dict()
worlds["esl"] = {"WorldModule": "esl.tutorial",
                 "WorldUIFunction": "ui"}
worlds["example"] = {"WorldModule": "file_system_example.examples",
                     "WorldUIFunction": "Example_ui"}


def world_information(key):
    return worlds.get(key, None)
