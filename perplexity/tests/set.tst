{
    "ResetModule": "examples",
    "ResetFunction": "Example24_reset",
    "TestItems": [
        {
            "Command": "/new examples.Example24_reset",
            "Expected": "State reset using examples.Example24_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "265a5921-b404-4896-9d8f-59305081820d"
        },
        {
            "Command": "files are large",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "331f555e-dd75-4836-88b3-6cde597eaebd"
        },
        {
            "Command": "which files are large",
            "Expected": "[File(name=/Desktop/the yearly budget.txt, size=10000000)]\n",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "aa892111-3d4a-477e-8ae2-858d95d9074c"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
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
            "Expected": "[File(name=/Desktop/the yearly budget.txt, size=10000000)]\n[File(name=/Desktop/blue, size=10000000)]\n",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "321bb542-a3bc-4cb1-b4f4-065aad48dce7"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "586671ad-5fd6-45e5-8236-64d521eb3faa"
        },
        {
            "Command": "a file is large",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e6ffb672-551a-48af-98de-34ff9b0c1a04"
        },
        {
            "Command": "/new examples.Example20_reset",
            "Expected": "State reset using examples.Example20_reset().",
            "Tree": null,
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
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "51c1f3fc-2555-407d-bb5b-29778adb2b22"
        },
        {
            "Command": "1 file is large",
            "Expected": "Yes, that is true.",
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
            "Expected": "[File(name=/Desktop/the yearly budget.txt, size=10000000)]\n[File(name=/Desktop/blue, size=10000000)]\n",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "19a53d3f-931d-40c4-85d2-389d76719410"
        },
        {
            "Command": "3 files are large",
            "Expected": "There are less than 3 large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(3,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "907f6e7b-4924-46d7-8555-263f9bf041ff"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
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
            "Expected": "There are more than 1 file",
            "Tree": "udef_q(x11,[_megabyte_n_1(x11,u18), card(20,e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],loc_nonsp(e2,x3,x11)))",
            "Enabled": true,
            "ID": "883c4f0e-5d43-4ab5-86a8-7aa2ebc1a46d"
        },
        {
            "Command": "/new examples.Example26_reset",
            "Expected": "State reset using examples.Example26_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "15382971-96f6-4a6e-ab2f-5db8672642d4"
        },
        {
            "Command": "which files are 20 mb?",
            "Expected": "(File(name=/Desktop/bigfile.txt, size=20000000),)\n(File(name=/Desktop/bigfile2.txt, size=20000000),)\n(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n",
            "Tree": "udef_q(x9,[_megabyte_n_1(x9,u16), card(20,e15,x9)],_which_q(x3,_file_n_of(x3,i8),loc_nonsp(e2,x3,x9)))",
            "Enabled": true,
            "ID": "05f835da-64f9-4c95-aabe-2dc8ba26bf73"
        },
        {
            "Command": "together, which files are 20 mb",
            "Comments": "Correctly returns single files in dist mode because it treats 'mb' as the collective that together is forcing",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n(File(name=/Desktop/bigfile.txt, size=20000000),)\n(File(name=/Desktop/bigfile2.txt, size=20000000),)\n",
            "Tree": "udef_q(x11,[_megabyte_n_1(x11,u18), card(20,e17,x11)],_which_q(x6,_file_n_of(x6,i10),[_together_p(e4,e2), loc_nonsp(e2,x6,x11)]))",
            "Enabled": true,
            "ID": "d4a1b97d-9fcf-448e-a429-4356eb3e171d"
        },
        {
            "Command": "which files together are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n",
            "Tree": "udef_q(x10,[_megabyte_n_1(x10,u17), card(20,e16,x10)],_which_q(x3,[_together_p(e9,x3), _file_n_of(x3,i8)],loc_nonsp(e2,x3,x10)))",
            "Enabled": true,
            "ID": "3333a366-a02a-4b4f-b874-671ef6b26b87"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "2cb61ffe-acb3-47ad-8cf5-1d3936c188ad"
        },
        {
            "Command": "a few files are large",
            "Expected": "There are less than a few large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "c4d1b82e-8be5-4b58-810d-97de24716ac5"
        },
        {
            "Command": "/new examples.Example26_reset",
            "Expected": "State reset using examples.Example26_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "2de5cbb2-de44-4857-bb0a-c1ece19cd4fc"
        },
        {
            "Command": "a few files are large",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "7bb89f92-03e9-400d-99b7-5d9d3fec52e9"
        },
        {
            "Command": "/new examples.Example27_reset",
            "Expected": "State reset using examples.Example27_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "b3665d6c-d098-4bce-86c3-031a9c04d67a"
        },
        {
            "Command": "a few files are large",
            "Expected": "There are more than a few large file",
            "Tree": "udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "2d32bbb8-f4b2-4069-a19d-0f67e0a4262e"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "110a3b3d-6725-448b-aed5-2b4ef2b6c0eb"
        },
        {
            "Command": "the files are large",
            "Expected": "That isn't true for all the file",
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
            "Expected": "There are more than the 3 file",
            "Tree": "_the_q(x3,[_file_n_of(x3,i10), card(3,e9,x3)],_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "d5ea50ee-c182-4db4-b2d8-83e1cf19b254"
        },
        {
            "Command": "the file is large",
            "Expected": "There is more than one the file",
            "Tree": "_the_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "02284161-0af3-45de-b4ba-8b6fbf67012a"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "State reset using examples.Example28_reset().",
            "Tree": null,
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
            "Expected": "There are less than a few file",
            "Tree": "udef_q(x10,[_megabyte_n_1(x10,u17), card(30,e16,x10)],udef_q(x3,[_file_n_of(x3,i9), _a+few_a_1(e8,x3)],loc_nonsp(e2,x3,x10)))",
            "Enabled": true,
            "ID": "7ff0f68e-4ca3-4085-a67f-1ae4b64a5287"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "64f3b027-5ae2-43cb-aaee-98b2fff80a4e"
        },
        {
            "Command": "which files are in folders",
            "Expected": "[File(name=/temp/59.txt, size=1000)]\n[File(name=/documents/file1.txt, size=1000)]\n[File(name=/Desktop/the yearly budget.txt, size=10000000)]\n[File(name=/Desktop/blue, size=10000000)]\n",
            "Tree": "udef_q(x9,_folder_n_of(x9,i14),_which_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "c412fa91-5229-4186-989f-f3513d5410f3"
        },
        {
            "Command": "which files are in a folder?",
            "Expected": "[File(name=/temp/59.txt, size=1000)]\n[File(name=/documents/file1.txt, size=1000)]\n[File(name=/Desktop/the yearly budget.txt, size=10000000)]\n[File(name=/Desktop/blue, size=10000000)]\n",
            "Tree": "_a_q(x9,_folder_n_of(x9,i14),_which_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "349d0ab3-36dd-4f81-a51b-705a0b888227"
        },
        {
            "Command": "/new examples.Example26_reset",
            "Expected": "State reset using examples.Example26_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "d6f55030-75f1-43a5-a8fc-7a913b503490"
        },
        {
            "Command": "which 2 files are in a folder?",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/bigfile.txt, size=20000000))\n(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/bigfile2.txt, size=20000000))\n(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n(File(name=/Desktop/bigfile.txt, size=20000000), File(name=/Desktop/bigfile2.txt, size=20000000))\n(File(name=/Desktop/bigfile.txt, size=20000000), File(name=/Desktop/blue, size=10000000))\n(File(name=/Desktop/bigfile2.txt, size=20000000), File(name=/Desktop/blue, size=10000000))\n",
            "Tree": "_a_q(x11,_folder_n_of(x11,i16),_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3a9b446e-1a73-49c6-a5c7-7a7d1847b359"
        },
        {
            "Command": "/new examples.Example26_reset",
            "Expected": "State reset using examples.Example26_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "df3dd43d-a0cf-4063-bf05-803d768a5e56"
        },
        {
            "Command": "which 2 files in a folder are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n[File(name=/Desktop/bigfile.txt, size=20000000)]\n[File(name=/Desktop/bigfile2.txt, size=20000000)]\n",
            "Tree": "_a_q(x12,_folder_n_of(x12,i17),udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],_which_q(x3,[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)],loc_nonsp(e2,x3,x18))))",
            "Enabled": true,
            "ID": "b20c612e-0359-48c8-b344-804c2144ed05"
        },
        {
            "Command": "which 2 files in a folder together are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n",
            "Tree": "_a_q(x12,_folder_n_of(x12,i17),udef_q(x19,[_megabyte_n_1(x19,u26), card(20,e25,x19)],_which_q(x3,[_file_n_of(x3,i10), _together_p(e18,x3), _in_p_loc(e11,x3,x12), card(2,e9,x3)],loc_nonsp(e2,x3,x19))))",
            "Enabled": true,
            "ID": "455fabb0-664d-4530-86ac-2a63a087db08"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "540d92f2-9561-43f9-9756-6e17f12d9bee"
        },
        {
            "Command": "the 2 files in a folder are 20 mb",
            "Expected": "Yes, that is true.",
            "Tree": "_a_q(x12,_folder_n_of(x12,i17),udef_q(x18,[_megabyte_n_1(x18,u25), card(20,e24,x18)],_the_q(x3,[_file_n_of(x3,i10), _in_p_loc(e11,x3,x12), card(2,e9,x3)],loc_nonsp(e2,x3,x18))))",
            "Enabled": true,
            "ID": "6d9105ef-59a6-42d0-9e11-08d96a530b54"
        },
        {
            "Command": "/new examples.Example31_reset",
            "Expected": "State reset using examples.Example31_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "e022e4fc-2b86-4f4f-ac51-8a800414672f"
        },
        {
            "Command": "which files are in 2 folders?",
            "Expected": "[File(name=/Desktop/file4.txt, size=10000000)]\n[File(name=/Desktop/file5.txt, size=10000000)]\n[File(name=/Desktop/file4.txt, size=10000000)]\n[File(name=/Desktop/file5.txt, size=10000000)]\n",
            "Tree": "udef_q(x9,[_folder_n_of(x9,i16), card(2,e15,x9)],_which_q(x3,_file_n_of(x3,i8),_in_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "55cb41a3-eb62-4162-aa8f-123a1cfacc8c"
        },
        {
            "Command": "1 file is in a folder together",
            "Expected": "I don't understand the way you are using: together",
            "Tree": "_a_q(x11,[_folder_n_of(x11,i16), _together_p(e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "61c8885b-063a-460e-9b8a-a25c01f31df4"
        },
        {
            "Command": "/new examples.Example26_reset",
            "Expected": "State reset using examples.Example26_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "20df35cc-f31e-45d7-8380-4c65ae1c3a2a"
        },
        {
            "Command": "which 2 large files are 20 mb",
            "Expected": "(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n[File(name=/Desktop/bigfile.txt, size=20000000)]\n[File(name=/Desktop/bigfile2.txt, size=20000000)]\n",
            "Tree": "udef_q(x12,[_megabyte_n_1(x12,u19), card(20,e18,x12)],_which_q(x3,[_file_n_of(x3,i11), _large_a_1(e10,x3), card(2,e9,x3)],loc_nonsp(e2,x3,x12)))",
            "Enabled": true,
            "ID": "3b8c9772-1b9b-4636-894b-4e42f0b23159"
        },
        {
            "Command": "the 4 large files are 20 mb",
            "Expected": "That isn't true for all the large 4 file",
            "Tree": "_the_q(x3,[_file_n_of(x3,i11), _large_a_1(e10,x3), card(4,e9,x3)],udef_q(x12,[_megabyte_n_1(x12,u19), card(20,e18,x12)],loc_nonsp(e2,x3,x12)))",
            "Enabled": true,
            "ID": "feb7f6d9-c583-4afc-b7d8-6614885db415"
        },
        {
            "Command": "/new examples.Example30_reset",
            "Expected": "State reset using examples.Example30_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "021c1bd5-fb80-45fb-9782-9faabb8aaae0"
        },
        {
            "Command": "which 2 files are in 2 folders?",
            "Expected": "[File(name=/Desktop/file2.txt, size=10000000)]\n[File(name=/Desktop/file3.txt, size=10000000)]\n[File(name=/documents/file4.txt, size=10000000)]\n[File(name=/documents/file5.txt, size=10000000)]\n",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "86773c14-37d1-4ace-9906-eea776f6b402"
        },
        {
            "Command": "/new examples.Example31_reset",
            "Expected": "State reset using examples.Example31_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "9ea1e81f-8dae-483e-b78a-787301ef6866"
        },
        {
            "Command": "which 2 files are in 2 folders",
            "Expected": "[File(name=/Desktop/file4.txt, size=10000000)]\n[File(name=/Desktop/file5.txt, size=10000000)]\n[File(name=/Desktop/file4.txt, size=10000000)]\n[File(name=/Desktop/file5.txt, size=10000000)]\n",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "e94d4a20-05d6-4242-bbc5-d16657e67374"
        }
    ]
}