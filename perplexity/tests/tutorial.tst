{
    "ResetModule": "examples",
    "ResetFunction": "Example18_reset",
    "TestItems": [
        {
            "Command": "/new examples.Example18_reset",
            "Expected": "State reset using examples.Example18_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "9d1434ed-a7ca-40e2-a3e8-e155278550a6"
        },
        {
            "Command": "a file is large",
            "Expected": "a file is not large",
            "Tree": "[['_a_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "d4a96bf6-4460-4dc2-927f-4081696c1d69"
        },
        {
            "Command": "delete a large file",
            "Expected": "There isn't 'a large file' in the system",
            "Tree": "[['pronoun_q', 'x3', [['pron', 'x3']], [['_a_q', 'x8', [['_file_n_of', 'x8', 'i14'], ['_large_a_1', 'e13', 'x8']], [['_delete_v_1', 'e2', 'x3', 'x8']]]]]]",
            "Enabled": true,
            "ID": "261f95e0-000e-4e71-8d55-a2d16862df3d"
        },
        {
            "Command": "which files are small?",
            "Expected": "File(name=file1.txt, size=1000000)\n",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_small_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "ff2e71f2-ee1b-48eb-94f7-01272a7af8fa"
        },
        {
            "Command": "delete a file",
            "Expected": "Done!",
            "Tree": "[['pronoun_q', 'x3', [['pron', 'x3']], [['_a_q', 'x8', [['_file_n_of', 'x8', 'i13']], [['_delete_v_1', 'e2', 'x3', 'x8']]]]]]",
            "Enabled": true,
            "ID": "2786d7f2-a49c-4bf5-8115-491707ddd790"
        },
        {
            "Command": "a file is large",
            "Expected": "There isn't 'a file' in the system",
            "Tree": "[['_a_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "b7cad993-ba10-47f1-8917-4c9e302d926b"
        },
        {
            "Command": "which files are small?",
            "Expected": "There isn't 'a file' in the system",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "32b52abe-a45d-41d7-8ea3-4eb83e90a93e"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example18_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "f1f577f2-ddfb-4f7b-9ea2-e58ce52277ff"
        },
        {
            "Command": "there is a folder",
            "Expected": "I don't know the words: be",
            "Tree": null,
            "Enabled": true,
            "ID": "35ad763d-92fb-4e79-b250-ef31cb918d84"
        },
        {
            "Command": "delete a folder",
            "Expected": "Done!",
            "Tree": "[['pronoun_q', 'x3', [['pron', 'x3']], [['_a_q', 'x8', [['_folder_n_of', 'x8', 'i13']], [['_delete_v_1', 'e2', 'x3', 'x8']]]]]]",
            "Enabled": true,
            "ID": "fca99a4c-e127-4a6a-ac21-6d3feeeab865"
        },
        {
            "Command": "/new examples.Example18a_reset",
            "Expected": "State reset using examples.Example18a_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "797a346f-d98a-4642-b933-f93e1d7d2323"
        },
        {
            "Command": "which file is very large?",
            "Expected": "File(name=file1.txt, size=20000000)\n",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_very_x_deg', 'e9', 'e2'], ['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "7f29b13c-aa0c-4d11-bc8d-ec9dcf598cac"
        },
        {
            "Command": "delete you",
            "Expected": "I can't delete you",
            "Tree": "[['pronoun_q', 'x8', [['pron', 'x8']], [['pronoun_q', 'x3', [['pron', 'x3']], [['_delete_v_1', 'e2', 'x3', 'x8']]]]]]",
            "Enabled": true,
            "ID": "3764ed0c-d85d-48ef-bd80-fdb6e5b85376"
        },
        {
            "Command": "he deletes a file",
            "Expected": "unexpected: I don't know the way you used: delete",
            "Tree": null,
            "Enabled": true,
            "ID": "141f6357-7d42-48f1-aa83-d7c0811b35c1"
        }
    ]
}