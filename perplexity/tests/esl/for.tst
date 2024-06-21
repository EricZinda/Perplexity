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
            "Command": "I want a table for my son",
            "Expected": "Johnny: Hey! That's not enough seats!",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),[_son_n_of(x14,i25), poss(e19,x14,x20)]),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "fb637129-e4f4-4527-be0d-e6631e4d3fcb"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "cd4b8ed5-f7aa-4554-aa99-670bc467f607"
        },
        {
            "Command": "i want a menu for me",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x14,pron(x14),pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "1861c0a8-40b9-44ed-9ead-027b05352742"
        },
        {
            "Command": "i want a menu for my son and me",
            "Expected": "Waiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: You already ordered a menu for you\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x14,def_explicit_q(x19,pronoun_q(x24,pron(x24),[_son_n_of(x19,i29), poss(e23,x19,x24)]),pronoun_q(x31,pron(x31),_and_c(x14,x19,x31))),pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "f0e425af-b527-4d04-bbda-9fca32e08fba"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "5222f761-aabd-4f22-a9ab-e4947baa480b"
        },
        {
            "Command": "I want a steak for 2",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_steak_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "7681ee53-5c07-49ac-8b96-3d6860c75be2"
        },
        {
            "Command": "I want a steak for 3",
            "Expected": "I'm not sure which steak for 3 thing you mean.",
            "Tree": "number_q(x14,card(3,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_steak_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "1ece99a5-80ee-41fa-a807-c28871dd2662"
        },
        {
            "Command": "I want a steak for 1",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "number_q(x14,card(1,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_steak_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "8b544110-8bc3-4b58-9c4c-a8b38a2175a8"
        },
        {
            "Command": "no",
            "Expected": "Johnny: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu? \nYou tell the waiter to ignore what you just ordered.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "76c0d5d7-e042-4c2f-a6aa-2d6b9d06fc57"
        },
        {
            "Command": "I want a steak for 1",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "number_q(x14,card(1,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_steak_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "e20a9e0d-a3bc-4051-b957-079353476fa7"
        },
        {
            "Command": "how much is the soup",
            "Expected": "4 dollars\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "64ef0380-b1b8-447b-83aa-d50e2f6a5aa4"
        },
        {
            "Command": "I want a soup for my son",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),[_son_n_of(x14,i25), poss(e19,x14,x20)]),pronoun_q(x3,pron(x3),_a_q(x8,[_soup_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a035f8a2-2719-4aed-a601-b96f384c8353"
        },
        {
            "Command": "I want a vegetarian dish for Johnny",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: Can I get you anything else?",
            "Tree": "proper_q(x16,named(Johnny,x16),pronoun_q(x3,pron(x3),_a_q(x8,[_dish_n_of(x8,i14), _for_p(e15,x8,x16), _vegetarian_a_1(e13,x8)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "da6923a2-db45-44d0-88a8-cf0e842f12c5"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a steak for you.\nWaiter: Here is a soup for Johnny.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "5ee8de39-54cf-47b0-8a38-7dff509880c6"
        },
        {
            "Command": "my steak is for 1",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x9,pron(x9),number_q(x14,card(1,x14,i20),def_explicit_q(x3,[_steak_n_1(x3), poss(e8,x3,x9)],_for_p(e2,x3,x14))))",
            "Enabled": true,
            "ID": "86ad8d69-a014-4e4a-9099-6c87bdd70156"
        },
        {
            "Command": "my steak is for 3",
            "Expected": "Host: No that is not true",
            "Tree": "pronoun_q(x9,pron(x9),number_q(x14,card(3,x14,i20),def_explicit_q(x3,[_steak_n_1(x3), poss(e8,x3,x9)],_for_p(e2,x3,x14))))",
            "Enabled": true,
            "ID": "d3726b90-3af5-491e-8aab-521915ab8fb1"
        },
        {
            "Command": "who ordered soup?",
            "Expected": "Johnny",
            "Tree": "which_q(x3,person(x3),udef_q(x8,_soup_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c78aeda0-1690-4e8f-b7fc-73aa0038c394"
        }
    ],
    "ElapsedTime": 40.99861
}