{
    "ResetModule": "examples",
    "ResetFunction": "Example25_reset",
    "TestItems": [
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "dd1ab5e6-431a-4098-b4a8-268586b7b9ee"
        },
        {
            "Command": "all files are in a folder",
            "Expected": "Yes, that is true.(there are more)",
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
        }
    ]
}