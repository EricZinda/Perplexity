{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a93e332f-00e8-4249-bfa1-95180dbd3a8f"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "6ed7a9ca-6f88-4c1c-9fbc-de93b4d7dd0f"
        },
        {
            "Command": "what are your specials",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you something to eat?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "6ecd843f-4675-4ed9-8e10-1e06055609b8"
        },
        {
            "Command": "what are your specials",
            "Expected": "soup\nsalad\npork",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "57d4c78e-29c7-48c6-b4a8-7a5ae33f05d0"
        },
        {
            "Command": "what is vegetarian",
            "Expected": "soup\n(among others)",
            "Tree": "which_q(x3,thing(x3),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "394d953d-4985-44b5-9145-7d9effa2cda2"
        },
        {
            "Command": "what are the vegetarian dishes",
            "Expected": "soup\nsalad",
            "Tree": "which_q(x3,thing(x3),_the_q(x8,[_dish_n_of(x8,i14), _vegetarian_a_1(e13,x8)],_be_v_id(e2,x3,x8)))",
            "Enabled": true,
            "ID": "117e2681-5df1-4694-8c3e-d32c36b73f8e"
        }
    ]
}