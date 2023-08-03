{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2ba0af2c-9d36-4c23-abc3-9112283310d7"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5463c147-27e5-4920-934b-c6bfddc3741c"
        },
        {
            "Command": "How much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "0c66d40d-000d-4f44-b15b-ec79e5bd018a"
        },
        {
            "Command": "How much is the salad?",
            "Expected": "3 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "5d7616ff-0fe6-482a-a57b-67ea07f9cf72"
        },
        {
            "Command": "I would like the salad",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "7a84fe83-a358-4884-932d-cf00e69eb5bb"
        },
        {
            "Command": "I would like the soup",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ad7a56d1-f75d-4cef-9649-99aa5aaae31d"
        },
        {
            "Command": "What did I order?",
            "Expected": "salad\nsoup",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f04f7d4e-c918-4d46-81f0-a4bf4044dae4"
        },
        {
            "Command": "I ordered salad and soup",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x13,_salad_n_1(x13),udef_q(x18,_soup_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_order_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "bd6b1750-5480-4661-a1d6-600bb7dbbc2a"
        }
    ]
}