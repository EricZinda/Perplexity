{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ca458224-ee3b-4026-abd1-162fdccae031"
        },
        {
            "Command": "I'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "773a6c5f-70a1-4900-9af0-b4e5d0620b3c"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you something to eat?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f5b87a2d-d97a-4ec5-a017-858a64d4f2c1"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "88f8b6e9-7601-46e1-9bb1-d91301a52faa"
        },
        {
            "Command": "I want the soup",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1746a509-05db-475b-b0ed-619fed5432bf"
        },
        {
            "Command": "my son wants the soup",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "3cf08778-3bbd-46b5-8aed-472b80b92b01"
        },
        {
            "Command": "no",
            "Expected": "Ok, I'll be right back with your meal.\nA few minutes go by and the robot returns with soup0 soup1.\nThe food is good, but nothing extraordinary.",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "93a49803-1e03-4f25-9aee-2efcd87e1fa0"
        },
        {
            "Command": "which dish do I have?",
            "Expected": "soup",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ecb032dd-3be2-4c8e-9b1c-1117b72f0554"
        }
    ]
}