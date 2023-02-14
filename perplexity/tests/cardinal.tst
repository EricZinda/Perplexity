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
        }
    ]
}