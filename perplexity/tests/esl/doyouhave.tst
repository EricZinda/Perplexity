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
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "dfaa005f-cf58-45d3-a744-68d8407ab28f"
        },
        {
            "Command": "what do you have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ea3f7879-3ea3-4231-8648-c87f3ff20592"
        },
        {
            "Command": "what specials do you have?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ddb396d5-8fc8-4994-8137-c9a13dd26db0"
        },
        {
            "Command": "what dishes do you have?",
            "Expected": "pork\nsoup\nsalad\nsteak\nchicken\nsalmon",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "dfd7cb6b-b4e6-46e9-bcb7-53b16e96755e"
        },
        {
            "Command": "what vegetarian dishes do you have?",
            "Expected": "soup\nsalad",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a0e93abc-0832-4dfe-b1a7-ba4214ee4319"
        },
        {
            "Command": "what meats do you have?",
            "Expected": "pork\nsteak\nchicken\nsalmon",
            "Tree": "_which_q(x5,_meat_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "87af8b68-309e-4aea-aa3f-ec421d2d7273"
        },
        {
            "Command": "what vegetarian meats do you have?",
            "Expected": "Host: There isn't such a vegetarian meat here",
            "Tree": "_which_q(x5,[_meat_n_1(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "ae7abcc5-6e6b-4d44-a0b4-897246bd70b6"
        },
        {
            "Command": "what smoked meat do you have?",
            "Expected": "pork",
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
    ]
}