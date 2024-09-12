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
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "dfaa005f-cf58-45d3-a744-68d8407ab28f"
        },
        {
            "Command": "what do you have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ea3f7879-3ea3-4231-8648-c87f3ff20592"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "082f5141-b2a0-4205-afa8-98c88075ef7d"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ddb396d5-8fc8-4994-8137-c9a13dd26db0"
        },
        {
            "Command": "what dishes do you have?",
            "Expected": [
                "pork\nsoup\nsalad\nsteak\nchicken\nsalmon\nWaiter: What can I get you?",
                "soup\nsalad\npork\nsalmon\nsteak\nchicken\nWaiter: What can I get you?"
            ],
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "dfd7cb6b-b4e6-46e9-bcb7-53b16e96755e"
        },
        {
            "Command": "what vegetarian dishes do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a0e93abc-0832-4dfe-b1a7-ba4214ee4319"
        },
        {
            "Command": "are any dishes vegetarian?",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "_any_q(x3,_dish_n_of(x3,i8),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "ed1b79b6-cb24-4ee3-ad22-72047d065a68"
        },
        {
            "Command": "are there any vegetarian dishes?",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "_any_q(x4,[_dish_n_of(x4,i10), _vegetarian_a_1(e9,x4)],_be_v_there(e2,x4))",
            "Enabled": true,
            "ID": "55c33452-0468-4075-b999-38e4420086b9"
        },
        {
            "Command": "do you have any vegetarian dishes?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8,i14), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d9ebe110-462e-493c-8de6-27f139026627"
        },
        {
            "Command": "Do you have any vegetarian dishes available?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8,i14), _available_a_to-for(e15,x8,u16), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d2bed2ef-2e52-4cd2-951f-c4085eb51b3e"
        },
        {
            "Command": "what meats do you have?",
            "Expected": [
                "pork\nsteak\nchicken\nsalmon\nWaiter: What can I get you?",
                "pork\nsalmon\nsteak\nchicken\nWaiter: What can I get you?"
            ],
            "Tree": "_which_q(x5,_meat_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "87af8b68-309e-4aea-aa3f-ec421d2d7273"
        },
        {
            "Command": "what vegetarian meats do you have?",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_meat_n_1(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ae7abcc5-6e6b-4d44-a0b4-897246bd70b6"
        },
        {
            "Command": "what smoked meat do you have?",
            "Expected": "Son: Wait, let's not order pork before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_meat_n_1(x5), _smoke_v_1(e9,i10,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "aecd6d6f-fc01-4ad3-8865-00273f7996a8"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "5d63f5ce-6532-40a0-8118-e42cd923740a"
        }
    ],
    "ElapsedTime": 16.26235
}