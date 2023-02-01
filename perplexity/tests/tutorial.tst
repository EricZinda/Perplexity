{
    "ResetModule": "examples",
    "ResetFunction": "Example19_reset",
    "TestItems": [
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
            "Expected": "File(name=/documents/file1.txt, size=1000000)\n",
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
            "Expected": "State reset using examples.Example19_reset().",
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
            "Command": "a file is deleted",
            "Expected": "I don't know the way you used: delete",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_very_x_deg', 'e9', 'e2'], ['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "7f29b13c-aa0c-4d11-bc8d-ec9dcf598cac"
        },
        {
            "Command": "which file is very small?",
            "Expected": "I don't understand the way you are using 'very' with 'small'",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_very_x_deg', 'e9', 'e2'], ['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "ce5adad4-4e72-4e1e-b42e-e2d03ab87a86"
        },
        {
            "Command": "a file is deleted",
            "Expected": "I don't know the way you used: delete",
            "Tree": "[['_which_q', 'x3', [['_file_n_of', 'x3', 'i8']], [['_very_x_deg', 'e9', 'e2'], ['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "5df6d756-ed91-4d18-b435-30110dcd8dba"
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
            "Expected": "I don't know the way you used: delete",
            "Tree": null,
            "Enabled": true,
            "ID": "141f6357-7d42-48f1-aa83-d7c0811b35c1"
        },
        {
            "Command": "/new examples.Example20_reset",
            "Expected": "State reset using examples.Example20_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "5eb557b0-97c5-483a-9498-e2772547caa1"
        },
        {
            "Command": "where am i",
            "Expected": "in /Desktop",
            "Tree": "[['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]]",
            "Enabled": true,
            "ID": "1c77c347-656b-4a14-9317-b319adb0fab4"
        },
        {
            "Command": "/new examples.Example21_reset",
            "Expected": "State reset using examples.Example21_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "81ba878f-56f5-41e6-820a-9fe181d25bc3"
        },
        {
            "Command": "where am i",
            "Expected": "in /Desktop",
            "Tree": "[['pronoun_q', 'x3', [['pron', 'x3']], [['which_q', 'x4', [['place_n', 'x4']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]]",
            "Enabled": true,
            "ID": "44fe6fc2-2d63-4893-a2ac-e59ca7c9fb85"
        },
        {
            "Command": "where is this folder",
            "Expected": "in /",
            "Tree": "[['which_q', 'x4', [['place_n', 'x4']], [['_this_q_dem', 'x3', [['_folder_n_of', 'x3', 'i13']], [['loc_nonsp', 'e2', 'x3', 'x4']]]]]]",
            "Enabled": true,
            "ID": "954a3dcf-10f9-42a0-943b-61364cc71c7e"
        },
        {
            "Command": "this folder is large",
            "Expected": "this folder is not large",
            "Tree": "[['_this_q_dem', 'x3', [['_folder_n_of', 'x3', 'i8']], [['_large_a_1', 'e2', 'x3']]]]",
            "Enabled": true,
            "ID": "e820409b-70ce-4331-80a2-6701fab73378"
        },
        {
            "Command": "/new examples.Example22_reset",
            "Expected": "State reset using examples.Example22_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "04bb3c68-2f72-4d68-9eab-969482c530a3"
        },
        {
            "Command": "what is large?",
            "Expected": "Folder(name=/Desktop, size=10000000)\nFile(name=/Desktop/file2.txt, size=10000000)\n",
            "Tree": "which_q(x3,thing(x3),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "8422a7fa-a85e-48fa-902e-6c85667c01c9"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example22_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "a333c133-2cde-4f90-a71c-f60589853b2a"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "File(name=/Desktop/file2.txt, size=10000000)\nFile(name=/Desktop/file3.txt, size=1000)\n",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2c28ec90-c629-4430-b549-867f0ec569a0"
        },
        {
            "Command": "what am i in?",
            "Expected": "Folder(name=/Desktop, size=10000000)\nFolder(name=/, size=0)\n",
            "Tree": "pronoun_q(x3,pron(x3),which_q(x5,thing(x5),_in_p_loc(e2,x3,x5)))",
            "Enabled": true,
            "ID": "25e8d164-7899-4861-beaa-075a3b479bcb"
        },
        {
            "Command": "is a file in this folder",
            "Expected": "Yes.",
            "Tree": "_this_q_dem(x9,_folder_n_of(x9,i14),_a_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "8b5f2598-1eaa-4a1b-a879-3019aa14417c"
        },
        {
            "Command": "is a folder in this folder",
            "Expected": "a folder is not in this folder",
            "Tree": "_this_q_dem(x9,_folder_n_of(x9,i14),_a_q(x3,_folder_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "52d8d2cd-d7dd-4a1f-8cd0-4dc2e41d8707"
        },
        {
            "Command": "which files are in this folder?",
            "Expected": "File(name=/Desktop/file2.txt, size=10000000)\nFile(name=/Desktop/file3.txt, size=1000)\n",
            "Tree": "_this_q_dem(x9,_folder_n_of(x9,i14),_which_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "ecfb6513-af04-4b08-9ab0-de6f27873473"
        },
        {
            "Command": "/new examples.Example23_reset",
            "Expected": "State reset using examples.Example23_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "4043a857-553d-4601-9235-ca34fc6e60a4"
        },
        {
            "Command": "\"blue\" is in this folder",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),proper_q(x8,[quoted(blue,i13), fw_seq(x8,i13)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "dfa7fc82-b238-4f94-8001-5f690181baf7"
        },
        {
            "Command": "what is in this 'blue'",
            "Expected": "thing is not in this 'blue'",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,[quoted(blue,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "34f4e321-b387-4e56-b2ed-3fec5a574cf5"
        },
        {
            "Command": "delete \"blue\"",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),proper_q(x8,[quoted(blue,i13), fw_seq(x8,i13)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8ad5cc45-0b32-4360-a06f-83db9d24f0d2"
        },
        {
            "Command": "\"blue\" is in this folder",
            "Expected": "'blue' is not in this folder",
            "Tree": "_this_q_dem(x10,_folder_n_of(x10,i15),proper_q(x3,[quoted(blue,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "7184c555-009b-474f-853d-5cff2eb459f2"
        },
        {
            "Command": "\"the yearly budget.txt\" is in this folder",
            "Expected": "Yes, that is true.",
            "Tree": "_this_q_dem(x15,_folder_n_of(x15,i20),proper_q(x3,[quoted(budget.txt,i9), quoted(yearly,i11), quoted(the,i10), fw_seq(x8,i10,i11), fw_seq(x3,x8,i9)],_in_p_loc(e2,x3,x15)))",
            "Enabled": true,
            "ID": "a3022350-209f-4a47-b916-47fec27a1d03"
        },
        {
            "Command": "delete \"the yearly budget.txt\"",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),proper_q(x8,[quoted(budget.txt,i14), quoted(yearly,i16), quoted(the,i15), fw_seq(x13,i15,i16), fw_seq(x8,x13,i14)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ed4e63f5-94e7-4814-a75e-3fca5111b119"
        },
        {
            "Command": "\"the yearly budget.txt\" is in this folder",
            "Expected": "'the yearly budget.txt' is not in this folder",
            "Tree": "_this_q_dem(x15,_folder_n_of(x15,i20),proper_q(x3,[quoted(budget.txt,i9), quoted(yearly,i11), quoted(the,i10), fw_seq(x8,i10,i11), fw_seq(x3,x8,i9)],_in_p_loc(e2,x3,x15)))",
            "Enabled": true,
            "ID": "4f09e0fa-11f0-4493-b78c-59b45fb110f5"
        },
        {
            "Command": "what is \"foo\" in?",
            "Expected": "'foo' was not found",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,[quoted(foo,i13), fw_seq(x3,i13)],_in_p_loc(e2,x3,x5)))",
            "Enabled": true,
            "ID": "767c57ee-5234-4c6d-9dce-9f8a2c789711"
        },
        {
            "Command": "what is in \"foo\"",
            "Expected": "'foo' was not found",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(foo,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cf9f7269-1dfe-439a-adc6-caa15dbc887f"
        },
        {
            "Command": "\"foo\" is in \"/documents\"",
            "Expected": "'foo' is not in '/documents'",
            "Tree": "proper_q(x10,[quoted(/documents,i15), fw_seq(x10,i15)],proper_q(x3,[quoted(foo,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "086f2827-5653-4d90-8fe8-a5b3986df029"
        },
        {
            "Command": "where is \"doesn't exist\"",
            "Expected": "'doesn\u2019t exist' was not found",
            "Tree": "which_q(x4,place_n(x4),proper_q(x3,[quoted(exist,i14), quoted(doesn\u2019t,i13), fw_seq(x3,i13,i14)],loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "cd5bbf5b-d4de-469b-b690-5e125dda5378"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example23_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "41d51bab-23a8-4169-93a7-365aef864641"
        },
        {
            "Command": "go to \"/documents\"",
            "Expected": "Done!",
            "Tree": "proper_q(x9,[quoted(/documents,i14), fw_seq(x9,i14)],pronoun_q(x3,pron(x3),[_to_p_dir(e8,e2,x9), _go_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "2db0658c-8aac-484f-b120-f9c43de91e26"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "File(name=/documents/file1.txt, size=1000)\n",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "10313c53-a01e-400e-aa74-b798db3fe3f4"
        },
        {
            "Command": "go to \"doesn't exist\"",
            "Expected": "'doesn\u2019t exist' was not found",
            "Tree": "proper_q(x9,[quoted(exist,i15), quoted(doesn\u2019t,i14), fw_seq(x9,i14,i15)],pronoun_q(x3,pron(x3),[_to_p_dir(e8,e2,x9), _go_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "9f36511c-6b12-40a4-99c9-b4a6765a5ecd"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example23_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "0b3ba5ef-4c0f-4fed-bfaa-45cda3a0ce09"
        },
        {
            "Command": "what is in \"/documents\"",
            "Expected": "File(name=/documents/file1.txt, size=1000)\n",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(/documents,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "805cdc7d-1391-40c9-a686-a6ea6c2c58f7"
        },
        {
            "Command": "delete \"file1.txt\" in \"/documents\"",
            "Expected": "Done!",
            "Tree": "proper_q(x16,[quoted(/documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[_in_p_loc(e15,x8,x16), quoted(file1.txt,i13), fw_seq(x8,i13)],_delete_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "f95d74c8-3b08-401e-bc70-7a5517eee968"
        },
        {
            "Command": "what is in \"/documents\"",
            "Expected": "thing is not in '/documents'",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(/documents,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "bc7ebed2-b20c-4426-b0d1-124ffe2a5dd0"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example23_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "688b1014-1849-42c3-9f6d-1eed9164ce64"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "File(name=/Desktop/the yearly budget.txt, size=10000000)\nFile(name=/Desktop/blue, size=1000)\n",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f519332-f958-470e-ae0c-28da1161c5e6"
        },
        {
            "Command": "copy \"file1.txt\" in \"/documents\"",
            "Expected": "Done!",
            "Tree": "proper_q(x16,[quoted(/documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[_in_p_loc(e15,x8,x16), quoted(file1.txt,i13), fw_seq(x8,i13)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "5a73a52a-fa97-4694-8120-8a47e0c99ce2"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "File(name=/Desktop/the yearly budget.txt, size=10000000)\nFile(name=/Desktop/blue, size=1000)\nFile(name=/Desktop/file1.txt, size=1000)\n",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b12b4de4-f6ec-4dee-811a-1a9f96003ea7"
        },
        {
            "Command": "/reset",
            "Expected": "State reset using examples.Example23_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "6aeec7a0-0b66-488f-bfc7-f15bcf81c024"
        },
        {
            "Command": "what is in \"\\>root111\"",
            "Expected": "Folder(name=/documents, size=0)\nFolder(name=/Desktop, size=10000000)\n",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\\\>work111,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "87db9431-d91b-492f-844e-919dac3a392f"
        }
    ]
}