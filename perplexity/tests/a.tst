{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e679d41e-af04-4f80-8192-5cbf08eb33af"
        },
        {
            "Command": "I want 2 steaks",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f412ffe0-207b-4b36-b8a4-b4e541ff3817"
        },
        {
            "Command": "what did I order",
            "Expected": "2 steak",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "18d4ddaa-a0b5-4c6e-be76-f52dc41dda77"
        }
    ]
}