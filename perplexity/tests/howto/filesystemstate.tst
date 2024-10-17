{
    "WorldName": "SimplestFileSystemStateExample",
    "TestItems": [
        {
            "Command": "/new hello_world.hello_world_FileSystemState.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2725fccc-1b69-4c22-a5ff-b4f0e8ecc806"
        },
        {
            "Command": "Hi!",
            "Expected": [
                "I don't know the words: Hi, Hi!",
                "I don't know the words: Hi!, Hi"
            ],
            "Tree": "None",
            "Enabled": true,
            "ID": "caacd9da-c95a-4520-a6d8-bebb3131e750"
        },
        {
            "Command": "Where am I?",
            "Expected": "(Folder(name=/Desktop, size=10000000),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "a19112ee-512c-4463-af7e-cb7b2485b7f4"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "060043c3-1400-4706-8fc8-c2e75d48a3d3"
        },
        {
            "Command": "which file is large?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "78adc7c0-eeec-4640-b935-8cbe63056747"
        },
        {
            "Command": "students are lifting a table",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x9,_table_n_1(x9),udef_q(x3,_student_n_of(x3,i8),_lift_v_cause(e2,x3,x9)))",
            "Enabled": true,
            "ID": "a8e30a54-c0ce-469d-b927-21b6d1bb0136"
        },
        {
            "Command": "a student is lifting a table",
            "Expected": "There is more than a student",
            "Tree": "_a_q(x9,_table_n_1(x9),_a_q(x3,_student_n_of(x3,i8),_lift_v_cause(e2,x3,x9)))",
            "Enabled": true,
            "ID": "e87687a9-1da9-41ff-9a2f-4b6faee908e0"
        },
        {
            "Command": "which students are lifting the table",
            "Expected": "('Elsa', 'Seo-Yun')",
            "Tree": "_which_q(x3,_student_n_of(x3,i8),_the_q(x9,_table_n_1(x9),_lift_v_cause(e2,x3,x9)))",
            "Enabled": true,
            "ID": "ed2f24f1-9693-42e7-9728-1c29717b9568"
        },
        {
            "Command": "a student is large",
            "Expected": "a student is not large",
            "Tree": "_a_q(x3,_student_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "c36401f5-22dd-4f35-8f0d-844a99318a29"
        },
        {
            "Command": "what file is large?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "782e71fa-a995-4539-b02a-a5eafdd17358"
        },
        {
            "Command": "what file is very large?",
            "Expected": "a file is not large",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),[_very_x_deg(e9,e2), _large_a_1(e2,x3)])",
            "Enabled": true,
            "ID": "6c6a4fb1-28e9-4360-9a9f-99c039c0f912"
        },
        {
            "Command": "a file is very large",
            "Expected": "a file is not large",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),[_very_x_deg(e9,e2), _large_a_1(e2,x3)])",
            "Enabled": true,
            "ID": "4a1109e4-b0af-419c-8bdd-34fdad1c8b8b"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "69ca2fb3-9223-4be7-a728-1b680e2ff970"
        },
        {
            "Command": "delete a large file",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_file_n_of(x8,i14), _large_a_1(e13,x8)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "266787c7-ad89-4a1f-81eb-cad84f5ea7b0"
        },
        {
            "Command": "a file is large",
            "Expected": "a file is not large",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "18ea01cf-2059-4b14-8e18-3c59f0028825"
        },
        {
            "Command": "where am I",
            "Expected": "(Folder(name=/Desktop, size=10000000),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "93a8b490-5964-4d0a-bb8d-140e37caa2a2"
        },
        {
            "Command": "where are you?",
            "Expected": "you is not in place",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "9d2b1c2b-e98f-49c1-8be7-6e951db1c189"
        },
        {
            "Command": "where is a file?",
            "Expected": "(Folder(name=/documents, size=0),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),_a_q(x3,_file_n_of(x3,i13),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "67ea05d3-5a9a-42f5-8c5d-964090a15ad6"
        },
        {
            "Command": "where is a folder?",
            "Expected": "(Folder(name=/, size=0),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),_a_q(x3,_folder_n_of(x3,i13),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "3678e81d-a0dc-4e10-990b-93b953b6f1c4"
        },
        {
            "Command": "go to a folder",
            "Expected": "Done!\n(there are more)",
            "Tree": "_a_q(x9,_folder_n_of(x9,i14),pronoun_q(x3,pron(x3),[_to_p_dir(e8,e2,x9), _go_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "3d43348a-7a51-4868-85b8-37533eda97f3"
        },
        {
            "Command": "where am I?",
            "Expected": "(Folder(name=/documents, size=0),)\n(there are more)",
            "Tree": "which_q(x4,place_n(x4),pronoun_q(x3,pron(x3),loc_nonsp(e2,x3,x4)))",
            "Enabled": true,
            "ID": "3baa1a40-ec44-4c49-9305-ec592bb6f75a"
        },
        {
            "Command": "do you have commands?",
            "Expected": "You can use the following commands: copy and go",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "318f604b-936d-4a56-a4f0-4db5cad0da7b"
        },
        {
            "Command": "which commands do you have?",
            "Expected": "You can use the following commands: copy and go",
            "Tree": "_which_q(x5,_command_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e01d3ac3-b5ba-4232-a3a3-f7ea9b146d6c"
        },
        {
            "Command": "do you have a command?",
            "Expected": "You can use the following commands: copy and go",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "319b05f5-cb8e-4347-9d7c-f8998e05d16f"
        },
        {
            "Command": "do you have 2 commands?",
            "Expected": "You can use the following commands: copy and go",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_command_n_1(x8), card(2,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d33c08b6-8bb7-4b82-85d8-4b41d774aa48"
        },
        {
            "Command": "do I have a command?",
            "Expected": "you do not have a command",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9c6a86a2-b1f5-40ef-b61e-19f4cc1e5a46"
        },
        {
            "Command": "do I have a file?",
            "Expected": "you do not have a file",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_file_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e2fd7162-0acb-4059-b9de-e48c80ab7613"
        },
        {
            "Command": "do you have a file?",
            "Expected": "us do not have a file",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_file_n_of(x8,i13),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "448092e7-cf8c-45d5-a9ed-80fbc1c893db"
        },
        {
            "Command": "did you have a command?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1497cfad-f020-41bd-9092-b4510979df0b"
        },
        {
            "Command": "Do you have 3 commands?",
            "Expected": "You can use the following commands: copy and go",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_command_n_1(x8), card(3,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8e019b22-4991-44f6-8c47-a959af25eff0"
        },
        {
            "Command": "Do you have many commands?",
            "Expected": "I don't know the words: many",
            "Tree": "None",
            "Enabled": true,
            "ID": "b79d6ed2-23da-4fcb-ab15-947678e11cc3"
        },
        {
            "Command": "Do you have several commands?",
            "Expected": "I don't know the words: several",
            "Tree": "None",
            "Enabled": true,
            "ID": "0478994c-582d-455f-bb44-fb02a1b6f71b"
        },
        {
            "Command": "did you have a command?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9b8aeb7b-ef47-4635-859e-edde2757bdc2"
        },
        {
            "Command": "you are having a command?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "7a52f01c-7f59-4fe8-ba5e-8c94ebfbed68"
        },
        {
            "Command": "Are you having a command?",
            "Expected": "I don't understand the way you are using: have",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_command_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "bacae01a-c07f-4a2e-b66b-782a651cd0d7"
        },
        {
            "Command": "create a file",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_file_n_of(x8,i13),_create_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "780b2bba-e3cc-4d2d-974c-1e222db956f3"
        },
        {
            "Command": "create a text file",
            "Expected": "Done!",
            "Tree": "udef_q(x14,_text_n_of(x14,i19),pronoun_q(x3,pron(x3),_a_q(x8,[_file_n_of(x8,i20), compound(e13,x8,x14)],_create_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "76dd77fa-e9ad-4cdb-9da2-f30b4d9e5b0c"
        }
    ],
    "ElapsedTime": 86.82993
}