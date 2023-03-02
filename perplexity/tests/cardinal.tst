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
            "Expected": "x3#462(0:460:463->0)[dist]=File(name=/Desktop/yellow.txt, size=10000000)\nx3#462(0:460:464->0)[dist]=File(name=/Desktop/green.txt, size=1000)\nx3#507(0:461:508->0)[dist]=File(name=/temp/red.txt, size=10000000)\nx3#507(0:461:509->0)[dist]=File(name=/temp/blue.txt, size=1000)\n\nand\n\nx3#480(0:460:481->0)[coll]=File(name=/Desktop/yellow.txt, size=10000000), x3#480(0:460:481->1)[coll]=File(name=/Desktop/green.txt, size=1000)\nx3#520(0:461:521->0)[coll]=File(name=/temp/red.txt, size=10000000), x3#520(0:461:521->1)[coll]=File(name=/temp/blue.txt, size=1000)\n",
            "Tree": "_which_q(x3,[_file_n_of(x3,i10), card(2,e9,x3)],udef_q(x11,[_folder_n_of(x11,i18), card(2,e17,x11)],_in_p_loc(e2,x3,x11)))",
            "Enabled": true,
            "ID": "cf6229f7-87be-4c3d-9820-3bc6d3150de4"
        }
    ]
}