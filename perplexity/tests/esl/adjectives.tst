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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
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
            "Command": "I want the grilled salmon",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _grill_v_1(e13,i14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "07526a10-6eaa-43f9-b1ed-25f12369342a"
        },
        {
            "Command": "what is grilled?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "8ffbcbd5-8527-4e9c-8351-d8c413e3eb04"
        },
        {
            "Command": "what is grilled?",
            "Expected": "salmon",
            "Tree": "which_q(x3,thing(x3),_grill_v_1(e2,i8,x3))",
            "Enabled": true,
            "ID": "ca2c198e-4b69-4a1d-a20d-bfa1dd9aa556"
        }
    ]
}