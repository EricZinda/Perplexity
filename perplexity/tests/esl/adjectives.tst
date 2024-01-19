{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9071a4e3-01d8-4452-b484-498ae0163de9"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "484a8e87-086c-4d49-a9c7-a5bd4f109aa9"
        },
        {
            "Command": "the salmon is grilled",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_salmon_n_1(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "53ba1fcf-81b1-4dc9-bca0-2735e71b1c93"
        },
        {
            "Command": "is the salmon grilled?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_salmon_n_1(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "ab1a2cce-d9ea-4f9d-917a-268f48cf72c9"
        },
        {
            "Command": "do you have the grilled salmon",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _grill_v_1(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "00535794-2db5-44cc-9bb8-47c95f1bd988"
        },
        {
            "Command": "what is grilled?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "8ffbcbd5-8527-4e9c-8351-d8c413e3eb04"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "587635f9-4727-49de-9aaf-ffed4a6fa579"
        },
        {
            "Command": "what is grilled?",
            "Expected": "salmon\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "ca2c198e-4b69-4a1d-a20d-bfa1dd9aa556"
        },
        {
            "Command": "the pork is smoked",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_pork_n_1(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "06920d5c-cc03-437a-9924-b5af58233f3e"
        },
        {
            "Command": "is the pork smoked?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_pork_n_1(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "81ff3323-9450-4546-9bd0-f07f2156fcab"
        },
        {
            "Command": "do you have the smoked pork",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_pork_n_1(x8), _smoke_v_1(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "356262cd-6d0e-4ea9-8f1d-7cb83a06ef11"
        },
        {
            "Command": "I want the grilled salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _grill_v_1(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "07526a10-6eaa-43f9-b1ed-25f12369342a"
        },
        {
            "Command": "I want the smoked pork",
            "Expected": "Son: Wait, let's not order pork before we know how much it costs.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_pork_n_1(x8), _smoke_v_1(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9b022abb-9691-4bc6-8993-e8d8fbee0952"
        },
        {
            "Command": "what is smoked?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "7190456b-3675-4585-a9c2-b95e7f7e0760"
        },
        {
            "Command": "what is smoked?",
            "Expected": "pork\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_smoke_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "6d0e52f0-86c7-407f-ad67-27a0286b1f62"
        },
        {
            "Command": "the chicken is roasted",
            "Expected": "Yes, that is true.",
            "Tree": "_the_q(x3,_chicken_n_1(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "d7de34b3-d2b0-45f9-81a9-464b49dfdad7"
        },
        {
            "Command": "is the chicken roasted?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_chicken_n_1(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "488094e5-e8d5-4eae-94f0-76d6bfbfec8c"
        },
        {
            "Command": "do you have the roasted chicken",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_chicken_n_1(x8), _roast_v_cause(e13,i14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9818d448-e378-4a12-9ab0-828be345f34b"
        },
        {
            "Command": "I want the roasted chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_chicken_n_1(x8), _roast_v_cause(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a69bd72f-0a97-423e-98e8-2947e8d8d5ab"
        },
        {
            "Command": "what is roasted?",
            "Expected": "chicken\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),_roast_v_cause(e2,i8,x3))",
            "Enabled": true,
            "ID": "affd8599-3ae9-43f7-bd7b-e53fb3eb7fcb"
        }
    ]
}