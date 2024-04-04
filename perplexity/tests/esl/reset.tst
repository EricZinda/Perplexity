{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a3cc4d3-60e5-48e4-a624-f63883ff0403"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "1880a138-af07-4949-8987-69dce82b538d"
        },
        {
            "Command": "how much is the soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "c1d523ec-7a6e-4477-95c4-a90161b3c98f"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "4aba975f-b500-41e8-91e9-840acb6f3987"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "fdacf2bb-8a92-4f6a-999e-79bf25c8b802"
        },
        {
            "Command": "what did we order",
            "Expected": [
                "chicken\nsoup",
                "soup\nchicken"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "aa2f35b6-f3a1-4152-af96-d84c3be87a7b"
        },
        {
            "Command": "can my son start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x10,pron(x10),def_explicit_q(x3,[_son_n_of(x3,i15), poss(e9,x3,x10)],[event_replace(u99,e2,e17), _start_v_over_able(e2,x3)]))",
            "Enabled": true,
            "ID": "a76a2269-48fc-4c97-bf9d-5cd0e63e8cba"
        },
        {
            "Command": "what did I order",
            "Expected": "chicken",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "aa70e474-70e8-4c3c-9d95-f591a8906b6b"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "9a979384-9e3a-4734-91a8-fcc0777c1962"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "cd90a597-6821-45fb-b65c-564157c4597c"
        },
        {
            "Command": "can we start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "9a34c284-6dda-426f-86a7-fc17d97b0258"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a4b5e42c-e427-4877-8fde-0b95a9ec949a"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "f8da4a84-5816-40eb-b9a7-ddb765b10aa0"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "8df1861a-c314-4cf0-baec-47b6e5afcab9"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d84c6a2c-4283-454e-80f1-612d9a3d65c9"
        },
        {
            "Command": "could we start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "4cda3658-8a91-4bed-aa59-f887e4dc135d"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "20e138da-2adf-469a-9b09-cc41c87d3f70"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "3b5c662a-9cb0-49f2-b059-8b938ebd7a22"
        },
        {
            "Command": "can you start over?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _start_v_over_able(e2,x3)])",
            "Enabled": true,
            "ID": "e92b611c-e75e-4bf3-9a0a-66ed90134583"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "30bfbe73-9bfa-4ca8-bb8c-8548f95bcd3d"
        },
        {
            "Command": "what did my son order",
            "Expected": "son ordered nothing",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "f037ab19-ceb5-4acd-972e-15dcadada49e"
        }
    ],
    "ElapsedTime": 16.42517
}