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
            "Expected": [
                3,
                [
                    "too many"
                ]
            ],
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
            "Expected": [
                0,
                [
                    "notEnough"
                ]
            ],
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
            "Expected": "1 file is not 20 megabyte",
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
            "Expected": "(File(name=/Desktop/bigfile.txt, size=20000000),)\n(File(name=/Desktop/the yearly budget.txt, size=10000000), File(name=/Desktop/blue, size=10000000))\n",
            "Tree": "udef_q(x9,[_megabyte_n_1(x9,u16), card(20,e15,x9)],_which_q(x3,_file_n_of(x3,i8),loc_nonsp(e2,x3,x9)))",
            "Enabled": true,
            "ID": "05f835da-64f9-4c95-aabe-2dc8ba26bf73"
        }
    ]
}