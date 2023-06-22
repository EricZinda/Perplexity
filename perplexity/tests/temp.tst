{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "709e3a5b-1243-4620-a9c4-a62567e87bd7"
        },
        {
            "Command": "I'd like a table'",
            "Expected": "How many in your party?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "32069f7b-2db8-40f7-806e-a7cc6e922567"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "udef_q(x4,[generic_entity(x4), card(2,e10,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "7c37d9dd-4bf2-4ceb-a304-8c1e010c619f"
        },
        {
            "Command": "I'd like 2 steaks",
            "Expected": "Son: Wait, we've spent $0 and all that food costs $20 so if we get all that, we won't be able to pay for it with $15. \nWaiter: Can I get you something to eat?",
            "Tree": "udef_q(x11,[_steak_n_1(x11), card(2,e17,x11)],pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "86193f43-66c8-44a4-8722-dc4573eaeb62"
        }
    ]
}