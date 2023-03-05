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
        }
    ]
}