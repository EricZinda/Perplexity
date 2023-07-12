{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9e1086d8-cfd2-4762-b52d-2e421301b1da"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "e6c96c5b-b8c3-4f1e-af5d-881bb0e491d9"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4a436537-1f34-4de5-8e2b-a4cb177c7605"
        },
        {
            "Command": "What are the specials?",
            "Expected": "The specials are <description>",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e9ec6d48-008b-4c51-82e2-3f8d8b844b2c"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3683bdd4-f7e4-419c-bc16-f5df21f5cc41"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b4d472d4-4e03-4787-9360-8cf5a2920847"
        },
        {
            "Command": "I want a salad",
            "Expected": "Son: Wait, let's not order that before we know how much it costs. \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ee8d866-b726-444f-9abd-ba2db97f8caf"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2e558271-ef87-41e2-a5ba-d67ea0b5e4a3"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Sorry, you got the last one of those. We don't have any more. Can I get you something else? \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ac9ca7b7-60b3-4d02-8b03-9fa62fb80095"
        },
        {
            "Command": "My son would like a salmon",
            "Expected": "Son: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x18,_salmon_n_1(x18),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "603ebce5-dcab-45a3-abdd-df45f4106a1b"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "db0eb32b-5205-40e8-a821-35975d4668b5"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "8d7e82ba-9d89-46b2-8532-8ca326bea794"
        },
        {
            "Command": "I would like the salmon",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_salmon_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3003a1eb-14b6-4dfe-9fe9-496d3a3e44a1"
        }
    ]
}