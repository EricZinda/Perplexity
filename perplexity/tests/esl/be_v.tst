{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a93e332f-00e8-4249-bfa1-95180dbd3a8f"
        },
        {
            "Command": "Soup is a vegetarian item",
            "Expected": "Yes, that is true.",
            "Tree": "udef_q(x3,_soup_n_1(x3),_a_q(x8,[_thing_n_of-about(x8,i14), _vegetarian_a_1(e13,x8)],_be_v_id(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f0ba7d25-284f-4264-91c7-87eceb97897b"
        },
        {
            "Command": "What is my son?",
            "Expected": [
                "son\nperson\nthing\n",
                "person\nthing\nson\n",
                "thing\nson\nperson\n",
                "person\nson\nthing\n",
                "thing\nperson\nson\n"
            ],
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_son_n_of(x8,i19), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "6ed7a9ca-6f88-4c1c-9fbc-de93b4d7dd0f"
        },
        {
            "Command": "My son is Johnny",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x9,pron(x9),proper_q(x15,named(Johnny,x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_be_v_id(e2,x3,x15))))",
            "Enabled": true,
            "ID": "a23b8045-864b-4378-8a6d-a49e826a46c4"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "ce35b48f-d9ed-4583-b517-a03922365580"
        },
        {
            "Command": "what are your specials",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "6ecd843f-4675-4ed9-8e10-1e06055609b8"
        },
        {
            "Command": "what are your specials",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "57d4c78e-29c7-48c6-b4a8-7a5ae33f05d0"
        },
        {
            "Command": "what are specials",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "69c689eb-7d14-4b54-a960-f0aff8c36c09"
        },
        {
            "Command": "what are the vegetarian dishes",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_the_q(x8,[_dish_n_of(x8,i14), _vegetarian_a_1(e13,x8)],_be_v_id(e2,x3,x8)))",
            "Enabled": true,
            "ID": "117e2681-5df1-4694-8c3e-d32c36b73f8e"
        },
        {
            "Command": "what is not soup",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "which_q(x3,thing(x3),neg(e10,udef_q(x9,_soup_n_1(x9),_be_v_id(e2,x3,x9))))",
            "Enabled": true,
            "ID": "1fca3d70-25aa-47ee-9bee-c8966287c24f"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "f84af69c-9e0d-48c3-a4e4-0bcac9204698"
        },
        {
            "Command": "what is not soup",
            "Expected": "pork\nsalad\nsteak\nchicken\nsalmon\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),neg(e10,udef_q(x9,_soup_n_1(x9),_be_v_id(e2,x3,x9))))",
            "Enabled": true,
            "ID": "29f3e374-7975-43f3-95b6-9c59327ddd34"
        }
    ],
    "ElapsedTime": 50.79633
}