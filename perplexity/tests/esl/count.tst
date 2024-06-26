{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "69c95107-36db-4bca-b2b2-ee7d0a2a1a0e"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "c2423433-1298-439a-abec-63e1ba72e8c8"
        },
        {
            "Command": "what are your specials?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "b99e57aa-97a2-45d6-882d-285bf8340661"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "fed26e8b-3635-4fe7-9c0e-a3bed7afe14c"
        },
        {
            "Command": "how many soups did I order",
            "Expected": "you did not order soup  \nWaiter: What can I get you?",
            "Tree": "which_q(x9,abstr_deg(x9),pronoun_q(x3,pron(x3),count(e14,x9,x5,udef_q(x5,_soup_n_1(x5),_order_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "cf08e533-f93d-4add-b484-0cc653537a10"
        },
        {
            "Command": "I want a soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d76232c5-713c-4697-8943-abf8c3a1a90d"
        },
        {
            "Command": "how many soups did I order",
            "Expected": "1\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "which_q(x9,abstr_deg(x9),pronoun_q(x3,pron(x3),count(e14,x9,x5,udef_q(x5,_soup_n_1(x5),_order_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "249bb4ea-e6d6-43e0-8b47-89b4707b7837"
        },
        {
            "Command": "I want a soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides 2 soups for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "46ea576a-5aea-4374-b2d8-2fd7816447f0"
        },
        {
            "Command": "how many soups did I order",
            "Expected": "2\nWaiter: Can I get you anything besides 2 soups for you?",
            "Tree": "which_q(x9,abstr_deg(x9),pronoun_q(x3,pron(x3),count(e14,x9,x5,udef_q(x5,_soup_n_1(x5),_order_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "594dff55-c9c3-4521-966c-ab306fd3bc41"
        },
        {
            "Command": "how much soup did I order",
            "Expected": "2\nWaiter: Can I get you anything besides 2 soups for you?",
            "Tree": "which_q(x9,abstr_deg(x9),pronoun_q(x3,pron(x3),count(e14,x9,x5,udef_q(x5,_soup_n_1(x5),_order_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "ef6b5235-1124-4bbd-8bd5-a4a9526e569d"
        },
        {
            "Command": "My son wants the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides 2 soups for you and a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "6d59232b-488b-4855-bcb8-e495df42f9d7"
        },
        {
            "Command": "how much soup did my son order",
            "Expected": "1\nWaiter: Can I get you anything besides 2 soups for you and a soup for Johnny?",
            "Tree": "which_q(x9,abstr_deg(x9),def_explicit_q(x3,pronoun_q(x21,pron(x21),[_son_n_of(x3,i26), poss(e20,x3,x21)]),count(e14,x9,x5,udef_q(x5,_soup_n_1(x5),_order_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "c5732829-03b9-42d6-9f2b-d2f325fc2ccc"
        }
    ],
    "ElapsedTime": 6.36543
}