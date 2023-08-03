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
            "Command": "I want soup and steak",
            "Expected": "Son: Wait, let's not order that before we know how much it costs. \nWaiter: Can I get you something to eat?",
            "Tree": "udef_q(x13,_soup_n_1(x13),udef_q(x18,_steak_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "f412ffe0-207b-4b36-b8a4-b4e541ff3817"
        }
    ]
}