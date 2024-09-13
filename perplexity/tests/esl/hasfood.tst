{
    "WorldName": "esl",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "773a6c5f-70a1-4900-9af0-b4e5d0620b3c"
        },
        {
            "Command": "What does the soup cost?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_soup_n_1(x3),_cost_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "88f8b6e9-7601-46e1-9bb1-d91301a52faa"
        },
        {
            "Command": "I want the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1746a509-05db-475b-b0ed-619fed5432bf"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9ce32c15-1cb4-4ab4-8a0a-43208883659c"
        },
        {
            "Command": "I'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3b66ebac-1293-42d8-bdb0-13cab45ed78d"
        },
        {
            "Command": "how much will the soup be?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "86599391-5eaa-4a47-b675-21e943e40e7d"
        },
        {
            "Command": "I want the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b9af4eb0-4d26-481a-82e4-9b97c1631251"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "cb184f9e-d501-4d10-a88f-9c73b274def9"
        },
        {
            "Command": "I'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "a0b9e7aa-64c2-4c2c-8623-0b6195d9653f"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f5b87a2d-d97a-4ec5-a017-858a64d4f2c1"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "9fb0166e-c701-48d9-b056-c53a827981c3"
        },
        {
            "Command": "I want the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e101dd32-e6b0-4c97-bdb6-282a28f39dfa"
        },
        {
            "Command": "my son wants the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you and a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "3cf08778-3bbd-46b5-8aed-472b80b92b01"
        },
        {
            "Command": "what did I order?",
            "Expected": "soup\nWaiter: Can I get you anything besides a soup for you and a soup for Johnny?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "b52783ed-8747-47bb-8887-781bdd132798"
        },
        {
            "Command": "what did my son order?",
            "Expected": "soup\nWaiter: Can I get you anything besides a soup for you and a soup for Johnny?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "8424d121-6c81-4bb3-a987-fb38d9335b73"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a soup for you.\nWaiter: Here is a soup for Johnny.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "93a49803-1e03-4f25-9aee-2efcd87e1fa0"
        },
        {
            "Command": "which dish do I have?",
            "Expected": "soup\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ecb032dd-3be2-4c8e-9b1c-1117b72f0554"
        },
        {
            "Command": "I have the soup",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "348f9121-461a-4097-b2e3-f4411106f565"
        },
        {
            "Command": "which dish does my son have?",
            "Expected": "soup\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),def_explicit_q(x3,pronoun_q(x15,pron(x15),[_son_n_of(x3,i20), poss(e14,x3,x15)]),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ea373e12-c8aa-4509-b489-bfaa87c1c6b5"
        }
    ],
    "ElapsedTime": 21.18443
}