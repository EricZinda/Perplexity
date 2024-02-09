from perplexity.utilities import import_function_from_names

worlds = dict()
worlds["esl"] = {"WorldModule": "esl.tutorial",
                 "WorldUIFunction": "ui"}
worlds["example"] = {"WorldModule": "file_system_example.examples",
                     "WorldUIFunction": "Example_ui"}


def world_information(key):
    return worlds.get(key, None)


def ui_from_world_name(world_name, user_output=None, debug_output=None):
    world_info = world_information(world_name)
    if world_info is not None:
        ui_function = import_function_from_names(world_info["WorldModule"], world_info["WorldUIFunction"])
        return ui_function(user_output=user_output, debug_output=debug_output)

