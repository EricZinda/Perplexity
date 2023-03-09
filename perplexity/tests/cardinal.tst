{
    "ResetModule": "examples",
    "ResetFunction": "Example23_reset",
    "TestItems": [
        {
            "Command": "1 file is in \"\\>documents\"",
            "Expected": "Yes, that is true.",
            "Tree": "proper_q(x11,[quoted(\\\\>documents,i16), fw_seq(x11,i16)],udef_q(x3,[_file_n_of(x3,i10), card(1,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "f134e1f9-c174-4702-85f8-5bb4882c06b8"
        },
        {
            "Command": "2 files are in \"\\>Desktop\"",
            "Expected": "Yes, that is true.",
            "Tree": "proper_q(x11,[quoted(\\\\>Desktop,i16), fw_seq(x11,i16)],udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5792843f-ef8f-4ebb-ad47-63490f05d852"
        },
        {
            "Command": "/new examples.Example25_reset",
            "Expected": "State reset using examples.Example25_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "8b392566-933e-41c2-8864-3134ede6e4f3"
        },
        {
            "Command": "2 files are in 1 folder",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(1,e17,x11)],udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "c640e4fe-64fb-4c66-907f-509384f63731"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "State reset using examples.Example28_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "281f35b6-4c3a-4c63-af8b-f0d85f14be00"
        },
        {
            "Command": "2 files are in two folders",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "c3bdb836-be85-43a6-baf0-bb0a94aea2a9"
        },
        {
            "Command": "which 2 files are in two folders?",
            "Expected": "Folder(name=/Desktop, size=0)\n     File(name=/Desktop/yellow.txt, size=10000000)\n     File(name=/Desktop/green.txt, size=1000)\n\nFolder(name=/temp, size=0)\n     File(name=/temp/red.txt, size=10000000)\n     File(name=/temp/blue.txt, size=1000)\n\n",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "cf6229f7-87be-4c3d-9820-3bc6d3150de4"
        },
        {
            "Command": "/new examples.Example29_reset",
            "Expected": "State reset using examples.Example29_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "65073020-56df-4bca-8922-95591fb75973"
        },
        {
            "Command": "which 2 files are in 2 folders?",
            "Expected": "Folder(name=/Desktop, size=0)\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/Desktop/blue, size=1000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/temp/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\nFolder(name=/temp, size=0)\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/Desktop/blue, size=1000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/temp/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\n",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "f6446427-e193-457f-bfc6-fb78db994e7f"
        },
        {
            "Command": "which 2 files are in 2 folders together",
            "Expected": "Folder(name=/Desktop, size=0)\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=1000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/blue, size=1000) together\n     File(name=/temp/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n\nFolder(name=/temp, size=0)\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=1000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/blue, size=1000) together\n     File(name=/temp/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n\n\nAnother answer is:\nFolder(name=/Desktop, size=0), Folder(name=/temp, size=0) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/Desktop/blue, size=1000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/the yearly budget.txt, size=10000000)\n\n     File(name=/Desktop/blue, size=1000)\n     File(name=/temp/blue, size=1000)\n\n     File(name=/temp/the yearly budget.txt, size=10000000)\n     File(name=/temp/blue, size=1000)\n\n\nAnother answer is:\nFolder(name=/Desktop, size=0), Folder(name=/temp, size=0) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=1000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/the yearly budget.txt, size=10000000) together\n     File(name=/Desktop/blue, size=1000), File(name=/temp/blue, size=1000) together\n     File(name=/temp/the yearly budget.txt, size=10000000), File(name=/temp/blue, size=1000) together\n\n",
            "Tree": "udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],[_together_p_state(e19,e2), _in_p_loc(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "9eb79f0e-44de-48cf-9247-716b77fea2ac"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "State reset using examples.Example28_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "c87a674c-6168-4cae-b104-d7d405d57ce5"
        },
        {
            "Command": "delete two files in this folder",
            "Expected": "Done!",
            "Tree": "_this_q_dem(x17,_folder_n_of(x17,i22),pronoun_q(x3,pron(x3),udef_q(x8,[_in_p_loc(e16,x8,x17), _file_n_of(x8,i15), card(2,e14,x8)],_delete_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "da0c8e66-f8eb-4335-aeb7-f29488c2ea1e"
        },
        {
            "Command": "what is in this folder?",
            "Expected": "thing is not in this folder",
            "Tree": "which_q(x3,thing(x3),_this_q_dem(x8,_folder_n_of(x8,i13),_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "247a1b8d-0125-4507-9ecd-ff4e53438c9f"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "State reset using examples.Example28_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "94a9f301-22e6-42df-a65d-c90083df8222"
        },
        {
            "Command": "delete 2 files in 2 folders together",
            "Expected": "Done!",
            "Tree": "udef_q(x17,[_folder_n_of(x17,i24), card(2,e23,x17)],pronoun_q(x3,pron(x3),udef_q(x8,[_in_p_loc(e16,x8,x17), _file_n_of(x8,i15), card(2,e14,x8)],[_together_p_state(e25,e2), _delete_v_1(e2,x3,x8)])))",
            "Enabled": true,
            "ID": "1b892616-b857-462e-96cb-4a59e79af905"
        },
        {
            "Command": "what is in \"\\>Desktop\"?",
            "Expected": "thing is not in '/Desktop'",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\\\>Desktop,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e18992e8-4f5e-45cb-9fc1-01f63cd875ac"
        },
        {
            "Command": "what is in \"\\>temp\"?",
            "Expected": "thing is not in '/temp'",
            "Tree": "which_q(x3,thing(x3),proper_q(x8,[quoted(\\\\>temp,i13), fw_seq(x8,i13)],_in_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4bf463fb-e340-4e0a-a092-bcef0f68ca80"
        },
        {
            "Command": "/new examples.Example28_reset",
            "Expected": "State reset using examples.Example28_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "56240649-99ed-40b3-885d-d84ff4bd45f7"
        },
        {
            "Command": "which 2 files are 10 megabytes",
            "Expected": "Measure:10 mb\n     File(name=/Desktop/yellow.txt, size=10000000)\n     File(name=/temp/red.txt, size=10000000)\n\n",
            "Tree": "udef_q(x11,[_megabyte_n_1(x11,u18), card(10,e17,x11)],_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],loc_nonsp(e2,x3,x11)))",
            "Enabled": true,
            "ID": "20927658-b149-423c-a512-34521bc8ebdf"
        },
        {
            "Command": "/new examples.Example30_reset",
            "Expected": "State reset using examples.Example30_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "0fb18ce9-2076-4343-9a6b-19ba9d572ac9"
        },
        {
            "Command": "which 2 files are 10 megabytes together",
            "Expected": "Measure:10 mb\n     File(name=/Desktop/yellow.txt, size=5000000), File(name=/temp/red.txt, size=5000000) together\n\n",
            "Tree": "card_with_scope(10,e17,x11,[_megabyte_n_1(x11,u18)],udef_q_cardinal(x11,thing(x11),card_with_scope(2,e9,x3,[_file_n_of(x3,i10)],_which_q_cardinal(x3,thing(x3),[_together_p(e19,x3), loc_nonsp(e2,x3,x11)]))))",
            "Enabled": true,
            "ID": "5627aacd-1ef6-488b-80c2-f7e1b1c25a73"
        },
        {
            "Command": "/new examples.Example30_reset",
            "Expected": "State reset using examples.Example30_reset().",
            "Tree": null,
            "Enabled": true,
            "ID": "dd6efb7a-43f4-42c8-a546-9135326bc0e0"
        },
        {
            "Command": "which 2 files are in this folder together?",
            "Expected": "File(name=/Desktop/yellow.txt, size=5000000), File(name=/Desktop/green.txt, size=1000) together\n",
            "Tree": "_this_q_dem(x11,_folder_n_of(x11,i16),card_with_scope(2,e9,x3,[_file_n_of(x3,i10)],_which_q_cardinal(x3,thing(x3),[_together_p_state(e17,e2), _in_p_loc(e2,x3,x11)])))",
            "Enabled": true,
            "ID": "b52e8e15-021e-40fe-8554-3b0f5e6693d4"
        }
    ]
}