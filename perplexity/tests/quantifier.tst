{
    "WorldName": "example",
    "TestItems": [
        {
            "Command": "/new file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "dd1ab5e6-431a-4098-b4a8-268586b7b9ee"
        },
        {
            "Command": "all files are in a folder",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x9,_folder_n_of(x9,i14),_all_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "ebd2248c-81e8-4598-8751-9590373e3beb"
        },
        {
            "Command": "all files are 10 mb",
            "Expected": "That isn't true for all all file",
            "Tree": "udef_q(x9,[_megabyte_n_1(x9,u16), card(10,e15,x9)],_all_q(x3,_file_n_of(x3,i8),loc_nonsp(e2,x3,x9)))",
            "Enabled": true,
            "ID": "97776178-2182-4413-95ab-aabc6d735cc7"
        },
        {
            "Command": "every file is in a folder",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x9,_folder_n_of(x9,i14),_every_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "125d9c17-ade2-4c51-a4de-fcd43c3f4261"
        },
        {
            "Command": "each file is in a folder",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x9,_folder_n_of(x9,i14),_each_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "fbff47c9-43c7-47b0-9ed1-2a4ee24a880a"
        },
        {
            "Command": "each file is large",
            "Expected": "That isn't true for all each file",
            "Tree": "_each_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "f01678d0-59d2-4515-a6e7-a278ac82d29e"
        },
        {
            "Command": "every file is large",
            "Expected": "That isn't true for all every file",
            "Tree": "_every_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "552f673b-9a66-46a7-83f6-a84ec12e56d5"
        },
        {
            "Command": "each and every file is large",
            "Expected": "That isn't true for all each and every file",
            "Tree": "_each+and+every_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "a080a2e9-b84d-4492-840b-56a8e33a89e1"
        }
    ],
    "ElapsedTime": 8.91698
}