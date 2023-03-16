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
            "Expected": [
                0,
                [
                    "notPlural"
                ]
            ],
            "Tree": "udef_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "331f555e-dd75-4836-88b3-6cde597eaebd"
        },
        {
            "Command": "which files are large",
            "Expected": [
                0,
                [
                    "notPlural"
                ]
            ],
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
            "Expected": "File(name=/Desktop/the yearly budget.txt, size=10000000)\nFile(name=/Desktop/blue, size=10000000)\n",
            "Tree": "_which_q(x3,_file_n_of(x3,i8),_large_a_1(e2,x3))",
            "Enabled": true,
            "ID": "321bb542-a3bc-4cb1-b4f4-065aad48dce7"
        }
    ]
}