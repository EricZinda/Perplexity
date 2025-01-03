{
    "WorldName": "example",
    "TestItems": [
        {
            "Command": "/new samples.file_system_example.examples.Example24_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "265a5921-b404-4896-9d8f-59305081820d"
        },
        {
            "Command": "files are large",
            "Expected": "There are less than 2 large file",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "331f555e-dd75-4836-88b3-6cde597eaebd"
        },
        {
            "Command": "which files are large",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "aa892111-3d4a-477e-8ae2-858d95d9074c"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "c362a5d4-7616-4f5e-a327-aea5ff140c85"
        },
        {
            "Command": "files are large",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "0be9e379-7e62-4516-8c4c-ae1b47c6eb20"
        },
        {
            "Command": "which files are large",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000),)(File(name=/Desktop/blue, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "321bb542-a3bc-4cb1-b4f4-065aad48dce7"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "586671ad-5fd6-45e5-8236-64d521eb3faa"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e6ffb672-551a-48af-98de-34ff9b0c1a04"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example20_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5ab6cda0-d667-498e-84fe-6fbd59be14ab"
        },
        {
            "Command": "a file is large",
            "Expected": "a file is not large",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "d2e97c97-96a8-4ad6-a4fd-9625577b2881"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "51c1f3fc-2555-407d-bb5b-29778adb2b22"
        },
        {
            "Command": "1 file is large",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "3ffe599b-e9fb-40d7-a32b-56fa35710574"
        },
        {
            "Command": "2 files are large",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e606990b-d627-4895-806d-0db06a40826b"
        },
        {
            "Command": "which 2 files are large",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000),)(File(name=/Desktop/blue, size=10000000),)",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "19a53d3f-931d-40c4-85d2-389d76719410"
        },
        {
            "Command": "3 files are large",
            "Expected": "There are less than 3 3 large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(3,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "907f6e7b-4924-46d7-8555-263f9bf041ff"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f20bff30-b68d-4781-8f04-3ad518a29ac5"
        },
        {
            "Command": "2 files are 20 mb",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x11,[_megabyte_n_1(x11,u18), card(20,e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],loc_nonsp(e2,x3,x11)))",
            "Enabled": true,
            "ID": "a736acb7-3eb3-4054-bd7b-6500e5f9c11d"
        },
        {
            "Command": "1 file is 20 megabytes",
            "Expected": "There is more than 1 file that is 20 megabyte",
            "Tree": "udef_q(x11,[_megabyte_n_1(x11,u18), card(20,e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],loc_nonsp(e2,x3,x11)))",
            "Enabled": true,
            "ID": "883c4f0e-5d43-4ab5-86a8-7aa2ebc1a46d"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "15382971-96f6-4a6e-ab2f-5db8672642d4"
        },
        {
            "Command": "which files are 20 mb?",
            "Expected": "(File(name=/Desktop/bigfile.txt, size=20000000),)(File(name=/Desktop/bigfile2.txt, size=20000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,[_megabyte_n_1(x9,u16), card(20,e15,x9)],loc_nonsp(e2,x3,x9)))",
            "Enabled": true,
            "ID": "05f835da-64f9-4c95-aabe-2dc8ba26bf73"
        },
        {
            "Command": "together, which files are 20 mb",
            "Comments": "Correctly returns single files in dist mode because it treats 'mb' as the collective that together is forcing",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))",
            "Tree": "_which_q(x6,_file_n_of(x6,i10),udef_q(x11,[_megabyte_n_1(x11,u18), card(20,e17,x11)],[_together_p(e4,e2), loc_nonsp(e2,x6,x11)]))",
            "Enabled": true,
            "ID": "d4a1b97d-9fcf-448e-a429-4356eb3e171d"
        },
        {
            "Command": "which files together are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))",
            "Tree": "_which_q(x3,[_file_n_of(x3,i8), _together_p(e9,x3)],udef_q(x10,[_megabyte_n_1(x10,u17), card(20,e16,x10)],loc_nonsp(e2,x3,x10)))",
            "Enabled": true,
            "ID": "3333a366-a02a-4b4f-b874-671ef6b26b87"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2cb61ffe-acb3-47ad-8cf5-1d3936c188ad"
        },
        {
            "Command": "a few files are large",
            "Expected": "There are less than 3 a few large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "c4d1b82e-8be5-4b58-810d-97de24716ac5"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2de5cbb2-de44-4857-bb0a-c1ece19cd4fc"
        },
        {
            "Command": "a few files are large",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "7bb89f92-03e9-400d-99b7-5d9d3fec52e9"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example27_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b3665d6c-d098-4bce-86c3-031a9c04d67a"
        },
        {
            "Command": "a few files are large",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "2d32bbb8-f4b2-4069-a19d-0f67e0a4262e"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "110a3b3d-6725-448b-aed5-2b4ef2b6c0eb"
        },
        {
            "Command": "the files are large",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "d0738761-c3cc-45ab-a754-29b4cc871fc8"
        },
        {
            "Command": "the large files are large",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,[_file_n_of(x3,i9), _large_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "4868231b-cc7e-4ee9-834d-c1c0ce486b69"
        },
        {
            "Command": "the 2 large files are large",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,[_file_n_of(x3,i11), _large_a_1(e10,x3), card(2,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "373004b4-16bd-4b58-99e1-c9dc0db87051"
        },
        {
            "Command": "the 3 files are large",
            "Expected": "There are less than 3 3 large file",
            "Tree": "_the_q(x3,[_file_n_of(x3,i10), card(3,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "d5ea50ee-c182-4db4-b2d8-83e1cf19b254"
        },
        {
            "Command": "the file is large",
            "Expected": "There is more than 1 file",
            "Tree": "_the_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "02284161-0af3-45de-b4ba-8b6fbf67012a"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example28_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "dc9cc1ac-40cd-4ea5-8cff-d620cd99f7a7"
        },
        {
            "Command": "a few files are 20 mb",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x10,[_megabyte_n_1(x10,u17), card(20,e16,x10)],udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],loc_nonsp(e2,x3,x10)))",
            "Enabled": true,
            "ID": "678dbe3f-6589-4d72-b1c9-34434445b00c"
        },
        {
            "Command": "a few files are 30 mb",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x10,[_megabyte_n_1(x10,u17), card(30,e16,x10)],udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],loc_nonsp(e2,x3,x10)))",
            "Enabled": true,
            "ID": "7ff0f68e-4ca3-4085-a67f-1ae4b64a5287"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "64f3b027-5ae2-43cb-aaee-98b2fff80a4e"
        },
        {
            "Command": "which files are in folders",
            "Expected": "(File(name=/temp/59.txt, size=1000),)(File(name=/documents/file1.txt, size=1000),)(File(name=/Desktop/the yearly budget.txt, size=10000000),)(File(name=/Desktop/blue, size=10000000),)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "c412fa91-5229-4186-989f-f3513d5410f3"
        },
        {
            "Command": "which files are in a folder?",
            "Expected": "(File(name=/temp/59.txt, size=1000),)(File(name=/documents/file1.txt, size=1000),)(File(name=/Desktop/the yearly budget.txt, size=10000000),)(File(name=/Desktop/blue, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_a_q(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "349d0ab3-36dd-4f81-a51b-705a0b888227"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d6f55030-75f1-43a5-a8fc-7a913b503490"
        },
        {
            "Command": "which 2 files are in a folder?",
            "Expected": "(File(name=/temp/59.txt, size=1000),)(File(name=/documents/file1.txt, size=1000),)\n(there are more)",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_a_q(x11,_folder_n_of(x11,i16),_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3a9b446e-1a73-49c6-a5c7-7a7d1847b359"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "df3dd43d-a0cf-4063-bf05-803d768a5e56"
        },
        {
            "Command": "/genall",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "b20c612e-0359-48c8-b344-804c2144ed05"
        },
        {
            "Command": "which 2 files in a folder are 20 mb",
            "Expected": "(File(name=/Desktop/bigfile.txt, size=20000000),)(File(name=/Desktop/bigfile2.txt, size=20000000),)\n(there are more)",
            "Tree": "_which_q(x3,_a_q(x12,_folder_n_of(x12,i17),[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)]),udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],loc_nonsp(e2,x3,x18)))",
            "Enabled": true,
            "ID": "a162e3b6-879e-46f7-8360-33d1b7764f1c"
        },
        {
            "Command": "which 2 files in a folder together are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n(there are more)",
            "Tree": "_which_q(x3,_a_q(x12,_folder_n_of(x12,i17),[_file_n_of(x3,i10), _together_p(e18,x3), _in_p_loc(e11,x3,x12), card(2,e9,x3)]),udef_q(x19,[_megabyte_n_1(x19,u26), card(20,e25,x19)],loc_nonsp(e2,x3,x19)))",
            "Enabled": true,
            "ID": "455fabb0-664d-4530-86ac-2a63a087db08"
        },
        {
            "Command": "/genall false",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "72ded20f-009e-46a1-b9fc-a81eccd0727b"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example25_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "540d92f2-9561-43f9-9756-6e17f12d9bee"
        },
        {
            "Command": "the 2 files in a folder are 20 mb",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x12,_folder_n_of(x12,i17),udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],_the_q(x3,[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)],loc_nonsp(e2,x3,x18))))",
            "Enabled": true,
            "ID": "6d9105ef-59a6-42d0-9e11-08d96a530b54"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example31_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "e022e4fc-2b86-4f4f-ac51-8a800414672f"
        },
        {
            "Command": "which files are in 2 folders?",
            "Expected": "(File(name=/Desktop/file4.txt, size=10000000),)(File(name=/Desktop/file5.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,[_folder_n_of(x9,i16), card(2,e15,x9)],_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "55cb41a3-eb62-4162-aa8f-123a1cfacc8c"
        },
        {
            "Command": "1 file is in a folder together",
            "Expected": "There is more than a folder together",
            "Tree": "_a_q(x11,[_folder_n_of(x11,i16), _together_p(e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "61c8885b-063a-460e-9b8a-a25c01f31df4"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "20df35cc-f31e-45d7-8380-4c65ae1c3a2a"
        },
        {
            "Command": "/genall",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "3b8c9772-1b9b-4636-894b-4e42f0b23159"
        },
        {
            "Command": "which 2 large files are 20 mb",
            "Expected": "(File(name=/Desktop/bigfile.txt, size=20000000),)(File(name=/Desktop/bigfile2.txt, size=20000000),)\n(there are more)",
            "Tree": "_which_q(x3,[_file_n_of(x3,i11), _large_a_1(e10,x3), card(2,e9,x3)],udef_q(x12,[_megabyte_n_1(x12,u19), card(20,e18,x12)],loc_nonsp(e2,x3,x12)))",
            "Enabled": true,
            "ID": "1834e609-27cf-4d33-8acf-8ee5b9f22f7c"
        },
        {
            "Command": "the 4 large files are 20 mb",
            "Expected": "There are less than 4 large 4 file that is 20 megabyte",
            "Tree": "udef_q(x12,[_megabyte_n_1(x12,u19), card(20,e18,x12)],_the_q(x3,[_file_n_of(x3,i11), _large_a_1(e10,x3), card(4,e9,x3)],loc_nonsp(e2,x3,x12)))",
            "Enabled": true,
            "ID": "feb7f6d9-c583-4afc-b7d8-6614885db415"
        },
        {
            "Command": "/genall false",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "b7412894-ade5-4d6b-8aa7-6d5e40cf9f3e"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example30_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "021c1bd5-fb80-45fb-9782-9faabb8aaae0"
        },
        {
            "Command": "which 2 files are in 2 folders?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)(File(name=/Desktop/file3.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "86773c14-37d1-4ace-9906-eea776f6b402"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example31_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9ea1e81f-8dae-483e-b78a-787301ef6866"
        },
        {
            "Command": "which 2 files are in 2 folders",
            "Expected": "(File(name=/Desktop/file4.txt, size=10000000),)(File(name=/Desktop/file5.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "e94d4a20-05d6-4242-bbc5-d16657e67374"
        },
        {
            "Command": "4 files are in a folder",
            "Expected": "There is more than a folder",
            "Tree": "_a_q(x11,_folder_n_of(x11,i16),udef_q(x3,[_file_n_of(x3,i10), card(4,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "526a5445-c826-40cc-8fbc-33a574b36461"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example33_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "c7d38990-0372-4a5f-b1a5-20f8002e032c"
        },
        {
            "Command": "a few files are in a folder together",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x10,_folder_n_of(x10,i15),udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],[_together_p(e16,x3), _in_p_loc(e2,x3,x10)]))",
            "Enabled": true,
            "ID": "c640b37a-26d2-42f0-ab14-4be856692f16"
        },
        {
            "Command": "4 files are in a folder",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "_a_q(x11,_folder_n_of(x11,i16),udef_q(x3,[_file_n_of(x3,i10), card(4,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "1a73a9fb-0c5e-49bc-8063-a85df202a70c"
        },
        {
            "Command": "which files are in a folder?",
            "Expected": "(File(name=/documents/file0.txt, size=10000000),)(File(name=/documents/file1.txt, size=10000000),)(File(name=/documents/file2.txt, size=10000000),)(File(name=/documents/file3.txt, size=10000000),)(File(name=/documents/file4.txt, size=10000000),)(File(name=/documents/file5.txt, size=10000000),)(File(name=/documents/file6.txt, size=10000000),)(File(name=/documents/file7.txt, size=10000000),)(File(name=/documents/file8.txt, size=10000000),)(File(name=/documents/file9.txt, size=10000000),)(File(name=/documents/file10.txt, size=10000000),)(File(name=/documents/file11.txt, size=10000000),)(File(name=/documents/file12.txt, size=10000000),)(File(name=/documents/file13.txt, size=10000000),)(File(name=/documents/file14.txt, size=10000000),)(File(name=/documents/file15.txt, size=10000000),)(File(name=/documents/file16.txt, size=10000000),)(File(name=/documents/file17.txt, size=10000000),)(File(name=/documents/file18.txt, size=10000000),)(File(name=/documents/file19.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_a_q(x9,_folder_n_of(x9,i14),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "6f118fcc-9f49-46b9-9703-bbcd95ca84d8"
        },
        {
            "Command": "the 2 files are in 3 folders",
            "Expected": "There are less than 3 3 folder",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(3,e17,x11)],_the_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "1a81e3da-b22d-4a11-b61e-4eb21ec94b34"
        },
        {
            "Command": "which 2 files in the folder are large?",
            "Expected": "(File(name=/documents/file0.txt, size=10000000),)(File(name=/documents/file1.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_the_q(x12,_folder_n_of(x12,i17),[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)]),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "34457434-0312-48e3-a93b-f2badc6fb7d4"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example26_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3bf6bd45-a9a1-44e9-be7d-336ac320952b"
        },
        {
            "Command": "2 files are large",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "5162b0c9-fa3e-4c94-abc3-04a62f8dfc68"
        },
        {
            "Command": "only 2 files are large",
            "Expected": "There are more than 2 2 large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i11), _only_x_deg(e5,e6), card(2,e6,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "29ebc2f2-3fe3-4e9e-b62b-58050d28a0ad"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example21_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "44ceda3b-5d3d-437e-9efb-e53caeb06e44"
        },
        {
            "Command": "delete a large file",
            "Expected": "Done!",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_file_n_of(x8,i14), _large_a_1(e13,x8)],_delete_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "aa254b8d-5139-4e99-8ecf-7272008c18f4"
        },
        {
            "Command": "which files are large?",
            "Expected": "files are not large",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "15e2683a-1847-462d-97b8-7e8ef2bb02fc"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example34_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3882d41b-15c8-44c3-9d65-78b1067338a5"
        },
        {
            "Command": "which file is large",
            "Expected": "(File(name=/Desktop/file1.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "8ee95506-fce8-4be8-9198-1712dd66efa7"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example36_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f2db86bb-5c2e-4288-8902-79956ae8eaea"
        },
        {
            "Command": "which 2 files in a folder are large?",
            "Expected": "(File(name=/Desktop/file2.txt, size=10000000),)(File(name=/documents/file4.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_a_q(x12,_folder_n_of(x12,i17),[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)]),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "105ed870-e509-4ba7-8e78-ea3991197c0a"
        },
        {
            "Command": "/new samples.file_system_example.examples.Example34_reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "8063e05b-15e7-4a1b-a284-b2df13c1c2f9"
        },
        {
            "Command": "the files are in one folder",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x9,[_folder_n_of(x9,i16), card(1,e15,x9)],_the_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "b39e93c7-d7a1-4681-858a-4a15ae4ddd45"
        },
        {
            "Command": "the files are in two folders",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x9,[_folder_n_of(x9,i16), card(2,e15,x9)],_the_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "a2a9c5eb-5be4-46b0-ad4d-d6da65b3a3f5"
        },
        {
            "Command": "the files are in three folders",
            "Expected": "Yes, that is true.\n(there are more)",
            "Tree": "udef_q(x9,[_folder_n_of(x9,i16), card(3,e15,x9)],_the_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "a73e0df7-7737-43a0-861b-cabd732b41eb"
        },
        {
            "Command": "the files are in four folders",
            "Expected": "There are less than 4 4 folder",
            "Tree": "udef_q(x9,[_folder_n_of(x9,i16), card(4,e15,x9)],_the_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "be27ecc5-7138-4ed0-8dd9-76f7272753df"
        },
        {
            "Command": "which files are in three folders?",
            "Expected": "(File(name=/Desktop/file1.txt, size=10000000),)(File(name=/Desktop/file2.txt, size=10000000),)(File(name=/documents/file3.txt, size=10000000),)(File(name=/documents/file4.txt, size=10000000),)\n(there are more)",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),udef_q(x9,[_folder_n_of(x9,i16), card(3,e15,x9)],_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "5d924bb8-b229-44f4-a13a-28118017708a"
        },
        {
            "Command": "/genall",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "089fbac4-1e08-45ad-a939-d36a5064f701"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "5d7c83a9-84b6-48cd-a96f-14bc100ed973"
        },
        {
            "Command": "'file1.txt' and 'file2.txt' are in a folder together",
            "Expected": "Yes, that is true.",
            "Tree": "proper_q(x15,[quoted(file2.txt,i20), fw_seq(x15,i20)],_a_q(x22,_folder_n_of(x22,i27),udef_q(x3,proper_q(x8,[quoted(file1.txt,i12), fw_seq(x8,i12)],_and_c(x3,x8,x15)),[_together_p(e28,x3), _in_p_loc(e2,x3,x22)])))",
            "Enabled": true,
            "ID": "4032f59f-5453-40ec-aea5-a6a04ea7edae"
        },
        {
            "Command": "/genall false",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "41812d13-f167-4d3b-af0d-04cc5188893f"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "a87685f0-bc29-4e81-ab6e-7df0ca84ad0f"
        }
    ],
    "ElapsedTime": 106.76485
}