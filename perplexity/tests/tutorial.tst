{
    "WorldName": "example",
    "TestItems": [
        {
            "Command": "/new file_system_example.examples.Example19_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "265a5921-b404-4896-9d8f-59305081820d"
        },
        {
            "Command": "a file is large",
            "Expected": "a file is not large",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "d4a96bf6-4460-4dc2-927f-4081696c1d69"
        },
        {
            "Command": "delete a large file",
            "Expected": "There isn't a large file in the system",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_file_n_of(x8,i14), _large_a_1(e13,x8)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "261f95e0-000e-4e71-8d55-a2d16862df3d"
        },
        {
            "Command": "which files are small?",
            "Expected": "There are less than 2 small file",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_small_a_1(e2,x3))",
            "Enabled": true,
            "ID": "ff2e71f2-ee1b-48eb-94f7-01272a7af8fa"
        },
        {
            "Command": "which file is small?",
            "Expected": "(File(name=/documents/file1.txt, size=1000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_small_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e5a337e8-57f7-4578-a93f-dd7274df4844"
        },
        {
            "Command": "delete a file",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_file_n_of(x8,i13),_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2786d7f2-a49c-4bf5-8115-491707ddd790"
        },
        {
            "Command": "a file is large",
            "Expected": "There isn't a file in the system",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "b7cad993-ba10-47f1-8917-4c9e302d926b"
        },
        {
            "Command": "which files are small?",
            "Expected": "There isn't a file in the system",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_small_a_1(e2,x3))",
            "Enabled": true,
            "ID": "32b52abe-a45d-41d7-8ea3-4eb83e90a93e"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f1f577f2-ddfb-4f7b-9ea2-e58ce52277ff"
        },
        {
            "Command": "delete a folder",
            "Expected": "Done!\n(there are more)",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_folder_n_of(x8,i13),_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fca99a4c-e127-4a6a-ac21-6d3feeeab865"
        },
        {
            "Command": "/new file_system_example.examples.Example18a_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "797a346f-d98a-4642-b933-f93e1d7d2323"
        },
        {
            "Command": "a file is deleted",
            "Expected": "I don't know the way you used: deleted",
            "Tree": "None",
            "Enabled": true,
            "ID": "7f29b13c-aa0c-4d11-bc8d-ec9dcf598cac"
        },
        {
            "Command": "which file is very small?",
            "Expected": "a file is not small",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),[_very_x_deg(e9,e2), _small_a_1(e2,x3)])",
            "Enabled": true,
            "ID": "ce5adad4-4e72-4e1e-b42e-e2d03ab87a86"
        },
        {
            "Command": "a file is deleted",
            "Expected": "I don't know the way you used: deleted",
            "Tree": "None",
            "Enabled": true,
            "ID": "5df6d756-ed91-4d18-b435-30110dcd8dba"
        },
        {
            "Command": "delete you",
            "Expected": "I can't delete you",
            "Tree": "pronoun_q(x8,pron(x8),pronoun_q(x3,pron(x3),_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3764ed0c-d85d-48ef-bd80-fdb6e5b85376"
        },
        {
            "Command": "he deletes a file",
            "Expected": "I don't know the way you used: deletes",
            "Tree": "None",
            "Enabled": true,
            "ID": "141f6357-7d42-48f1-aa83-d7c0811b35c1"
        },
        {
            "Command": "/new file_system_example.examples.Example20_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5eb557b0-97c5-483a-9498-e2772547caa1"
        },
        {
            "Command": "where am i",
            "Expected": "(Folder(name=/Desktop, size=0),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "1c77c347-656b-4a14-9317-b319adb0fab4"
        },
        {
            "Command": "/new file_system_example.examples.Example21_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "81ba878f-56f5-41e6-820a-9fe181d25bc3"
        },
        {
            "Command": "where am i",
            "Expected": "(Folder(name=/Desktop, size=0),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "44fe6fc2-2d63-4893-a2ac-e59ca7c9fb85"
        },
        {
            "Command": "where is this folder",
            "Expected": "(Folder(name=/, size=0),)",
            "Tree": "which_q(x4,place_n(x4),_this_q_dem(x3,_folder_n_of(x3,i13),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "954a3dcf-10f9-42a0-943b-61364cc71c7e"
        },
        {
            "Command": "this folder is large",
            "Expected": "this folder is not large",
            "Tree": "_this_q_dem(x3,_folder_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e820409b-70ce-4331-80a2-6701fab73378"
        },
        {
            "Command": "/new file_system_example.examples.Example22_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "04bb3c68-2f72-4d68-9eab-969482c530a3"
        },
        {
            "Command": "what is large?",
            "Expected": "(Folder(name=/Desktop, size=10000000),)\n(there are more)",
            "Tree": "which_q(x3,thing(x3),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "8422a7fa-a85e-48fa-902e-6c85667c01c9"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a333c133-2cde-4f90-a71c-f60589853b2a"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)\n(there are more)",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2c28ec90-c629-4430-b549-867f0ec569a0"
        },
        {
            "Command": "what am i in?",
            "Expected": "(Folder(name=/Desktop, size=10000000),)(Folder(name=/, size=0),)",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_in_p_loc(e2,x3,x5)))",
            "Enabled": true,
            "ID": "25e8d164-7899-4861-beaa-075a3b479bcb"
        },
        {
            "Command": "is a file in this folder",
            "Expected": "Yes.\n(there are more)",
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
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)(File(name=/Desktop/file3.txt, size=1000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_this_q_dem(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "ecfb6513-af04-4b08-9ab0-de6f27873473"
        },
        {
            "Command": "/new file_system_example.examples.Example23_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4043a857-553d-4601-9235-ca34fc6e60a4"
        },
        {
            "Command": "\"blue\" is in this folder",
            "Expected": "Yes, that is true.",
            "Tree": "_this_q_dem(x10,_folder_n_of(x10,i15),proper_q(x3,[quoted(blue,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "dfa7fc82-b238-4f94-8001-5f690181baf7"
        },
        {
            "Command": "what is in this 'blue'",
            "Expected": "a thing is not in this 'blue'",
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
            "Tree": "_this_q_dem(x15,_folder_n_of(x15,i20),proper_q(x3,[quoted(budget.txt,i9), quoted(yearly,i11), quoted(the,i10), fw_seq(i8,i10,i11), fw_seq(x3,i8,i9)],_in_p_loc(e2,x3,x15)))",
            "Enabled": true,
            "ID": "a3022350-209f-4a47-b916-47fec27a1d03"
        },
        {
            "Command": "delete \"the yearly budget.txt\"",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),proper_q(x8,[quoted(budget.txt,i14), quoted(yearly,i16), quoted(the,i15), fw_seq(i13,i15,i16), fw_seq(x8,i13,i14)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ed4e63f5-94e7-4814-a75e-3fca5111b119"
        },
        {
            "Command": "\"the yearly budget.txt\" is in this folder",
            "Expected": "'the yearly budget.txt' is not in this folder",
            "Tree": "_this_q_dem(x15,_folder_n_of(x15,i20),proper_q(x3,[quoted(budget.txt,i9), quoted(yearly,i11), quoted(the,i10), fw_seq(i8,i10,i11), fw_seq(x3,i8,i9)],_in_p_loc(e2,x3,x15)))",
            "Enabled": true,
            "ID": "4f09e0fa-11f0-4493-b78c-59b45fb110f5"
        },
        {
            "Command": "what is \"foo\" in?",
            "Expected": "'foo' is not in a thing",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,[quoted(foo,i13), fw_seq(x3,i13)],_in_p_loc(e2,x3,x5)))",
            "Enabled": true,
            "ID": "767c57ee-5234-4c6d-9dce-9f8a2c789711"
        },
        {
            "Command": "what is in \"foo\"",
            "Expected": "'foo' can't contain things",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(foo,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cf9f7269-1dfe-439a-adc6-caa15dbc887f"
        },
        {
            "Command": "\"foo\" is in \"/documents\"",
            "Expected": "'foo' is not in '/documents'",
            "Tree": "proper_q(x10,[quoted(\\>documents,i15), fw_seq(x10,i15)],proper_q(x3,[quoted(foo,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "086f2827-5653-4d90-8fe8-a5b3986df029"
        },
        {
            "Command": "where is \"doesn't exist\"",
            "Expected": "'doesn\u2019t exist' is not in place",
            "Tree": "which_q(x4,place_n(x4),proper_q(x3,[quoted(exist,i14), quoted(doesn\u2019t,i13), fw_seq(x3,i13,i14)],loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "cd5bbf5b-d4de-469b-b690-5e125dda5378"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "41d51bab-23a8-4169-93a7-365aef864641"
        },
        {
            "Command": "go to \"/documents\"",
            "Expected": "You are now in Folder(name=/documents, size=0)",
            "Tree": "proper_q(x9,[quoted(\\>documents,i14), fw_seq(x9,i14)],pronoun_q(x3,pron(x3),[_to_p_dir(e8,e2,x9), _go_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "2db0658c-8aac-484f-b120-f9c43de91e26"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "(File(name=/documents/file1.txt, size=1000),)",
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
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0b3ba5ef-4c0f-4fed-bfaa-45cda3a0ce09"
        },
        {
            "Command": "what is in \"/documents\"",
            "Expected": "(File(name=/documents/file1.txt, size=1000),)",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\>documents,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "805cdc7d-1391-40c9-a686-a6ea6c2c58f7"
        },
        {
            "Command": "delete \"file1.txt\" in \"/documents\"",
            "Expected": "Done!",
            "Tree": "proper_q(x16,[quoted(\\>documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(file1.txt,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_delete_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "f95d74c8-3b08-401e-bc70-7a5517eee968"
        },
        {
            "Command": "what is in \"/documents\"",
            "Expected": "a thing is not in '/documents'",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\>documents,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "bc7ebed2-b20c-4426-b0d1-124ffe2a5dd0"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "688b1014-1849-42c3-9f6d-1eed9164ce64"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000),)\n(there are more)",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4f519332-f958-470e-ae0c-28da1161c5e6"
        },
        {
            "Command": "copy \"file1.txt\" in \"/documents\"",
            "Expected": "Done!",
            "Tree": "proper_q(x16,[quoted(\\>documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(file1.txt,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "5a73a52a-fa97-4694-8120-8a47e0c99ce2"
        },
        {
            "Command": "\"file1.txt\" is in this folder",
            "Expected": "Yes, that is true.",
            "Tree": "_this_q_dem(x10,_folder_n_of(x10,i15),proper_q(x3,[quoted(file1.txt,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "b12b4de4-f6ec-4dee-811a-1a9f96003ea7"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6aeec7a0-0b66-488f-bfc7-f15bcf81c024"
        },
        {
            "Command": "what is in \"\\>root111\"",
            "Expected": "(File(name=/documents/file1.txt, size=1000),)\n(there are more)",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\>root111,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "87db9431-d91b-492f-844e-919dac3a392f"
        },
        {
            "Command": "/new file_system_example.examples.Example24_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "292119f9-27f4-4bea-9f64-46ec589f07b5"
        },
        {
            "Command": "go to \"\\>documents\"",
            "Expected": "You are now in Folder(name=/documents, size=0)",
            "Tree": "proper_q(x9,[quoted(\\>documents,i14), fw_seq(x9,i14)],pronoun_q(x3,pron(x3),[_to_p_dir(e8,e2,x9), _go_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "bedac8b5-c170-423b-82bf-1e1c0fe5c199"
        },
        {
            "Command": "copy \"\\>temp\\>59.txt\" in \"\\>documents\"",
            "Expected": "'/temp/59.txt' in '/documents' is not in '/documents'",
            "Tree": "proper_q(x16,[quoted(\\>documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(\\>temp\\>59.txt,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "c7a1db52-5b8c-4b5c-b2e3-d4696a9d7193"
        },
        {
            "Command": "\"59.txt\" is in this folder",
            "Expected": "'59.txt' is not in this folder",
            "Tree": "_this_q_dem(x10,_folder_n_of(x10,i15),proper_q(x3,[quoted(59.txt,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "b29a3cab-f351-4021-b5a0-0791beca3007"
        },
        {
            "Command": "/new file_system_example.examples.Example23_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "1b73ed22-576e-48c9-b837-2986d664c627"
        },
        {
            "Command": "what is in '\\>documents'",
            "Expected": "(File(name=/documents/file1.txt, size=1000),)",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\>documents,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3ddf1b4f-8ee5-4659-ab7b-1ba4b2235221"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000),)\n(there are more)",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "35917912-d515-4f69-8a28-f313804fb234"
        },
        {
            "Command": "copy 'blue' in '\\>documents'",
            "Expected": "'blue' in '/documents' is not in '/documents'",
            "Tree": "proper_q(x16,[quoted(\\>documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(blue,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a25651b5-b4b2-4b40-a2b3-945f6ece746c"
        },
        {
            "Command": "'blue' is in '\\>documents'",
            "Expected": "'blue' is not in '/documents'",
            "Tree": "proper_q(x10,[quoted(\\>documents,i15), fw_seq(x10,i15)],proper_q(x3,[quoted(blue,i8), fw_seq(x3,i8)],_in_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "8cad0fce-3ce7-4d96-a384-606ef10fd11f"
        },
        {
            "Command": "where is a dog",
            "Expected": "a dog is not in place",
            "Tree": "which_q(x4,place_n(x4),_a_q(x3,_dog_n_1(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "88b0aa71-c1a3-47b1-bc8b-393bef1b8d33"
        },
        {
            "Command": "where is a book?",
            "Expected": "a book is not in place",
            "Tree": "which_q(x4,place_n(x4),_a_q(x3,_book_n_of(x3,i13),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "cf288c47-6395-4970-b543-62da22c74703"
        },
        {
            "Command": "please",
            "Expected": "Yes, that is true.",
            "Tree": "_please_v_1(e2,i3,i4)",
            "Enabled": true,
            "ID": "ed22ce42-3d7e-4b07-bfa2-3f6a48e2a2ff"
        },
        {
            "Command": "/new file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d07949c2-d346-40ce-92b6-febd84996a20"
        },
        {
            "Command": "\"blue\" and \"bigfile.txt\" are in this folder",
            "Expected": "Yes, that is true.",
            "Tree": "proper_q(x15,[quoted(bigfile.txt,i20), fw_seq(x15,i20)],_this_q_dem(x22,_folder_n_of(x22,i27),udef_q(x3,proper_q(x8,[quoted(blue,i12), fw_seq(x8,i12)],_and_c(x3,x8,x15)),_in_p_loc(e2,x3,x22))))",
            "Enabled": true,
            "ID": "b34be073-7412-4ad4-9da7-a584e3255ecb"
        },
        {
            "Command": "\"blue\" and \"59.txt\" are in this folder",
            "Expected": "'blue', '59.txt' (all together) are not in this folder",
            "Tree": "proper_q(x15,[quoted(59.txt,i20), fw_seq(x15,i20)],_this_q_dem(x22,_folder_n_of(x22,i27),udef_q(x3,proper_q(x8,[quoted(blue,i12), fw_seq(x8,i12)],_and_c(x3,x8,x15)),_in_p_loc(e2,x3,x22))))",
            "Enabled": true,
            "ID": "0a18a408-843e-4852-9e9b-547f8cfeb375"
        },
        {
            "Command": "\"bigfile.txt\" and \"bigfile2.txt\" are large",
            "Expected": "Yes, that is true.",
            "Tree": "proper_q(x15,[quoted(bigfile2.txt,i20), fw_seq(x15,i20)],udef_q(x3,proper_q(x8,[quoted(bigfile.txt,i12), fw_seq(x8,i12)],_and_c(x3,x8,x15)),_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "579f7805-b3e1-4a76-93c9-b485a1bb3642"
        },
        {
            "Command": "\"bigfile.txt\" and \"59.txt\" are large",
            "Expected": "a 'bigfile.txt', '59.txt' (all together) are not large",
            "Tree": "proper_q(x15,[quoted(59.txt,i20), fw_seq(x15,i20)],udef_q(x3,proper_q(x8,[quoted(bigfile.txt,i12), fw_seq(x8,i12)],_and_c(x3,x8,x15)),_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "8e760db8-a939-4f26-a6a5-c82896108357"
        },
        {
            "Command": "/new file_system_example.examples.Example38_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d0a05f0f-a999-4adb-9fb7-83bd3727ad8f"
        },
        {
            "Command": "which files are in folders?",
            "Expected": "I cannot respond to this",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "9a02fd1d-81fb-40d5-a7bd-15add7c6ab15"
        },
        {
            "Command": "/new file_system_example.examples.Example39_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "aea30b9e-de33-490d-8920-a77ec169a136"
        },
        {
            "Command": "which files are in folders",
            "Expected": "('fakefile0',)('fakefile1',)('fakefile2',)('fakefile3',)('fakefile4',)('fakefile5',)('fakefile6',)('fakefile7',)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "75d771c6-b11a-4c34-a3ee-9495aa385c07"
        },
        {
            "Command": "/new file_system_example.examples.Example40_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8fd63e9e-605b-45be-946e-047d5023af3f"
        },
        {
            "Command": "copy \"file4.txt\" in \"\\>documents\"",
            "Expected": "'file4.txt' in '/documents' is not in '/documents'",
            "Tree": "proper_q(x16,[quoted(\\>documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(file4.txt,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "67a6caf5-6b4d-4ad0-bdd9-fd5054f4c71f"
        },
        {
            "Command": "copy \"file5.txt\" in \"documents\"",
            "Expected": "I cannot copy that",
            "Tree": "proper_q(x16,[quoted(documents,i21), fw_seq(x16,i21)],pronoun_q(x3,pron(x3),proper_q(x8,[quoted(file5.txt,i13), fw_seq(x8,i13), _in_p_loc(e15,x8,x16)],_copy_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "1a169fd6-1915-4c2a-bf7e-9f9b0d34ebaa"
        },
        {
            "Command": "/new file_system_example.examples.Example41_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "695e8ec0-08b8-4811-addb-a566fc711845"
        },
        {
            "Command": "a file is in this folder",
            "Expected": "Could you be more specific?",
            "Tree": "_this_q_dem(x9,_folder_n_of(x9,i14),_a_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "5902e55a-2d11-44bf-b86d-6c0af4a16e83"
        }
    ],
    "ElapsedTime": 200.95375
}