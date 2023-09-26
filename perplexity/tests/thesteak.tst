{
    "ResetModule": "esl.tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "1dc7b8e0-1dbf-40c2-ab63-1b5015fdf9ec"
        },
        {
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "bbdd77cc-3cd9-4819-8c65-d1d892c13b98"
        },
        {
            "Command": "I want the steak",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ab6cf71d-b5e2-4755-9baa-d167b617535d"
        },
        {
            "Command": "I ordered the steak",
            "Expected": "There is more than the steak",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4e377bae-9b15-425b-ac6d-39b777d469de"
        }
    ]
}