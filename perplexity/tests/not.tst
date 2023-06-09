{
    "ResetModule": "examples",
    "ResetFunction": "Example29_reset",
    "TestItems": [
        {
            "Command": "/new examples.Example29_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2725fccc-1b69-4c22-a5ff-b4f0e8ecc806"
        },
        {
            "Command": "files are large",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "c4ab1df8-9ffb-42a6-9fda-dd56afca3fd0"
        },
        {
            "Command": "/runparse 0,1",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "4c44735a-2178-479b-a0c1-c7464c60467b"
        },
        {
            "Command": "files are not large",
            "Expected": "That isn't true",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),neg(e9,_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "43536245-921b-4a43-a57d-980d455f07f2"
        },
        {
            "Command": "/runparse 0,0",
            "Expected": "That isn't true",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),neg(e9,_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "f2bd9557-6c4e-4714-a355-7a458c44aac6"
        },
        {
            "Command": "files are not large",
            "Expected": "That isn't true",
            "Tree": "neg(e9,udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "e9a380ed-3d6a-4e7b-9f0b-d17d947d9d68"
        },
        {
            "Command": "/runparse 1,1",
            "Expected": "That isn't true",
            "Tree": "neg(e9,udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "b839a136-1b33-418b-add7-a6ff824dc56f"
        },
        {
            "Command": "files are not large",
            "Expected": "That isn't true",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),neg(e2,_large_a_1(e11,x3)))",
            "Enabled": true,
            "ID": "7147beda-8540-4e3f-89ff-2a7d151fc22d"
        },
        {
            "Command": "/runparse",
            "Expected": "That isn't true",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),neg(e2,_large_a_1(e11,x3)))",
            "Enabled": true,
            "ID": "04eb4045-3cc0-4bf2-892a-931561614cbd"
        },
        {
            "Command": "a file is not large",
            "Expected": "That isn't true",
            "Tree": "neg(e9,_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "ad36aee8-3362-498b-a32c-4770a1a37497"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5f940c11-9891-4c2d-830e-59e7a936e73e"
        },
        {
            "Command": "which files in this folder are not large?",
            "Expected": "That isn't true",
            "Tree": "_which_q(x3,_this_q_dem(x10,_folder_n_of(x10,i15),[_file_n_of(x3,i8), _in_p_loc(e9,x3,x10)]),neg(e16,_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "f048ade0-0f33-4181-bc5e-b4b8376268a0"
        },
        {
            "Command": "/new examples.Example27_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "345401ee-1396-4f4c-999e-d6bc96f2fa6f"
        },
        {
            "Command": "which files are not in this folder?",
            "Expected": "(File(name=/temp/59.txt, size=1000),)(File(name=/documents/file1.txt, size=1000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_this_q_dem(x12,_folder_n_of(x12,i17),neg(e9,_in_p_loc(e2,x3,x12))))",
            "Enabled": true,
            "ID": "165915b2-ca79-4230-980a-4c0ed477bfeb"
        },
        {
            "Command": "/new examples.Example27_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b42e40ad-2bea-4029-b72f-086b38f50a22"
        },
        {
            "Command": "which files not in this folder are not large?",
            "Expected": "(File(name=/temp/59.txt, size=1000),)(File(name=/documents/file1.txt, size=1000),)",
            "Tree": "_which_q(x3,_this_q_dem(x13,_folder_n_of(x13,i18),[_file_n_of(x3,i8), neg(e9,_in_p_loc(e12,x3,x13))]),neg(e19,_large_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "e1378c08-0c89-4c6b-8abd-1f294aceeb04"
        },
        {
            "Command": "which folder are files not in?",
            "Expected": "(Folder(name=/, size=0),)",
            "Tree": "_which_q(x5,_folder_n_of(x5,i9),udef_q(x3,_file_n_of(x3,i14),neg(e15,_in_p_loc(e2,x3,x5))))",
            "Enabled": true,
            "ID": "a3498188-b338-4e7c-99cc-f0bcff661159"
        }
    ]
}