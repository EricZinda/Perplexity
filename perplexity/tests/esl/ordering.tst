{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "91a85b2d-3b81-4954-85d0-9786ac6cb8d0"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e679d41e-af04-4f80-8192-5cbf08eb33af"
        },
        {
            "Command": "I want to eat a steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_eat_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "fb104052-8d82-44ab-bd0f-e4f4e54ca565"
        },
        {
            "Command": "my son wants to eat soup",
            "Expected": "Son: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x18,_soup_n_1(x18),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_eat_v_1_request(e2,x3,x18))))",
            "Enabled": true,
            "ID": "59241cdb-9064-4e87-b1c4-79267672615a"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "c1681d6a-53da-4ae5-8b4e-2f1e29313a11"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "66a31486-44bc-4082-b8b8-315966971c33"
        },
        {
            "Command": "I will order the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "dceb55ad-1632-4ba6-b201-020e04e26113"
        },
        {
            "Command": "We will order two waters",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything besides a steak and a water for you and a water for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_water_n_1(x8), card(2,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "00b573f9-37b5-4d1a-8741-6a76ccb75288"
        },
        {
            "Command": "Just some water for now, please",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything besides a steak and 2 waters for you and a water for Johnny?",
            "Tree": "_please_a_1(i19,def_implicit_q(x13,[time_n(x13), _now_a_1(e18,x13)],[_some_q(x5,[_water_n_1(x5), _for_p(e12,x5,x13)],unknown(e2,x5)), _just_x_deg(e7,u8)]))",
            "Enabled": true,
            "ID": "edaf4c2e-7031-4467-af1d-58f9faf90b9a"
        },
        {
            "Command": "We would both like menus",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "udef_q(x12,_menu_n_1(x12),pronoun_q(x3,pron(x3),[_both_a_1(i9,e2), _want_v_1(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "9358572e-164d-4d4b-83f7-88bfd18e80a0"
        },
        {
            "Command": "I'd like to order a menu for johnny",
            "Expected": "Waiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "_a_q(x14,proper_q(x20,named(Johnny,x20),[_menu_n_1(x14), _for_p(e19,x14,x20)]),pronoun_q(x3,pron(x3),_order_v_1_request(e13,x3,x14)))",
            "Enabled": true,
            "ID": "14a455aa-94e6-46d5-9fb6-b93b72188a9b"
        },
        {
            "Command": "That's all",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "no_standalone(e2)",
            "Enabled": true,
            "ID": "c5149153-9c2e-4fd7-bc50-1e4bde3d1020"
        },
        {
            "Command": "That's it",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "pronoun_q(x8,pron(x8),no_standalone(e2))",
            "Enabled": true,
            "ID": "e5661a8d-6376-418b-9f44-6a28a543592b"
        },
        {
            "Command": "That's all for the moment",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "_the_q(x14,_moment_n_1(x14),no_standalone(e2))",
            "Enabled": true,
            "ID": "f71ee648-63ac-4243-91ca-aa941a4cbef4"
        },
        {
            "Command": "That's it for the moment",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "pronoun_q(x8,pron(x8),_the_q(x14,_moment_n_1(x14),no_standalone(e2)))",
            "Enabled": true,
            "ID": "6fa3c9a9-ea4c-4318-b5ed-fc9ef0de6d67"
        },
        {
            "Command": "Nope that's it",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "_nope_a_1(i4,pronoun_q(x11,pron(x11),no_standalone(e2)))",
            "Enabled": true,
            "ID": "2fd65857-702b-4285-97d0-89b08decca67"
        },
        {
            "Command": "Nothing",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: Can I get you anything besides a steak, 2 waters, and a menu for you and a water and a menu for Johnny?",
            "Tree": "udef_q(x4,_nothing_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "21060508-e9a9-4a0d-aaf9-44785556b7de"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a3cc4d3-60e5-48e4-a624-f63883ff0403"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "9eebc75d-729a-4cda-b623-176f2fb007a3"
        },
        {
            "Command": "what is my order?",
            "Expected": "Nothing\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_order_n_of(x3), poss(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "e3c26e28-39e7-47cc-bfb2-cba28f48cb1f"
        },
        {
            "Command": "I want 2 steaks for lunch",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "udef_q(x16,_dish_n_of(x16),pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), _for_p(e15,x8,x16), card(2,e14,x8)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "53c1ba1a-7f52-4c70-b852-8e4fcf397e0a"
        },
        {
            "Command": "My order is one steak",
            "Expected": "There is more than 1 steak\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x14,[_steak_n_1(x14), card(1,e20,x14)],def_explicit_q(x3,[_order_n_of(x3), poss(e8,x3,x9)],_be_v_id(e2,x3,x14))))",
            "Enabled": true,
            "ID": "960b07fe-942d-4654-93f2-5c065888ab0a"
        },
        {
            "Command": "My order is two steaks",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x14,[_steak_n_1(x14), card(2,e20,x14)],def_explicit_q(x3,[_order_n_of(x3), poss(e8,x3,x9)],_be_v_id(e2,x3,x14))))",
            "Enabled": true,
            "ID": "121f854a-efb4-447f-b774-7532df6eedbc"
        },
        {
            "Command": "what is my order",
            "Expected": "2 steak\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_order_n_of(x3), poss(e13,x3,x14)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "9468312e-4b6f-40ea-ba76-2c6e6f7d0e45"
        },
        {
            "Command": "That's all for now",
            "Expected": "Johnny: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu? \nYou tell the waiter to ignore what you just ordered.\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,[time_n(x14), _now_a_1(e19,x14)],no_standalone(e2))",
            "Enabled": true,
            "ID": "b45a8499-47d3-4ef3-8813-915fe3cdda42"
        },
        {
            "Command": "That's it for now",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x8,pron(x8),def_implicit_q(x14,[time_n(x14), _now_a_1(e19,x14)],no_standalone(e2)))",
            "Enabled": true,
            "ID": "d6042a80-ea0d-4290-8e85-b09c16eb7b44"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a21cd75d-2110-475e-b315-5ca0cbf00d37"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e64275f7-3d17-4b44-a40a-10600fddfdee"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "082d7d3e-6087-44b3-907b-3b1c6f46348c"
        },
        {
            "Command": "My son needs a vegetarian dish",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x15,[_dish_n_of(x15,i21), _vegetarian_a_1(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_need_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "a7408b9b-7dc9-4d73-9006-0d37d4ffff0d"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "370f3289-cd51-4997-b346-4ac878ca28f7"
        },
        {
            "Command": "a vegetarian meal",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: What can I get you?",
            "Tree": "_a_q(x4,[_dish_n_of(x4), _vegetarian_a_1(e9,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "b20fd1cc-05ca-409d-810a-ab9284c0f9f7"
        },
        {
            "Command": "My son needs something vegetarian",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_some_q(x15,[thing(x15), _vegetarian_a_1(e20,x15)],def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_need_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "d0be4224-6142-416e-adc7-e30364846d24"
        },
        {
            "Command": "and I'll have the roasted chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you?",
            "Tree": "_the_q(x11,[_chicken_n_1(x11), _roast_v_cause(e16,i17,x11)],pronoun_q(x7,pron(x7),[event_replace(u99,e5,e2), _have_v_1(e5,x7,x11)]))",
            "Enabled": true,
            "ID": "0b467c65-c266-45f3-a8bd-9b4ff1dddf6f"
        },
        {
            "Command": "and how much is the soup?",
            "Expected": "4 dollars\nWaiter: Can I get you anything besides a chicken for you?",
            "Tree": "which_q(x12,abstr_deg(x12),_the_q(x18,_soup_n_1(x18),count(e16,x12,x7,udef_q(x7,generic_entity(x7),[event_replace(u99,e5,e2), _be_v_id(e5,x18,x7)]))))",
            "Enabled": true,
            "ID": "6d40569e-a739-43ef-a0c4-090e7b5f55b6"
        },
        {
            "Command": "I'll have the Grilled Salmon for myself",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything besides a chicken and a salmon for you?",
            "Tree": "pronoun_q(x16,pron(x16),pronoun_q(x3,pron(x3),_the_q(x8,[_salmon_n_1(x8), _for_p(e15,x8,x16), _grill_v_1(e13,i14,x8)],_have_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "b4ff0fd6-8cac-4ddb-a0b0-5885c7c71d8f"
        },
        {
            "Command": "and salmon",
            "Expected": "Son: Wait, we already spent $19 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a chicken and a salmon for you?",
            "Tree": "udef_q(x10,_salmon_n_1(x10),udef_q(x4,generic_entity(x4),[_and_c(x4,u9,x10), unknown(e2,x4)]))",
            "Enabled": true,
            "ID": "e0e2cf41-859b-4724-a6ab-f0ed316ece07"
        },
        {
            "Command": "what did we order?",
            "Expected": "Host: Nothing.\nWaiter: Can I get you anything besides a chicken and a salmon for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "fd743d50-17c2-4097-adef-8e252b58ebe6"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "087c0bc7-9003-4d1d-9bca-c78a42c415ff"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "63b80562-70b0-4885-804e-151b73d850c8"
        },
        {
            "Command": "for my son, I'll have the roasted chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything besides a chicken for Johnny?",
            "Tree": "pronoun_q(x11,pron(x11),pronoun_q(x3,pron(x3),_the_q(x21,[_chicken_n_1(x21), _roast_v_cause(e26,i27,x21)],def_explicit_q(x5,[_son_n_of(x5,i16), poss(e10,x5,x11)],[_for_p(e4,e2,x5), _have_v_1(e2,x3,x21)]))))",
            "Enabled": true,
            "ID": "3c03fc87-432d-4481-b06b-1efa3defa634"
        },
        {
            "Command": "for my son, please get the salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything besides a chicken and a salmon for Johnny?",
            "Tree": "pronoun_q(x11,pron(x11),pronoun_q(x3,pron(x3),_the_q(x23,_salmon_n_1(x23),def_explicit_q(x5,[_son_n_of(x5,i16), poss(e10,x5,x11)],[polite(please,i18,e2), _for_p(e4,e2,x5), _get_v_1(e2,x3,x23)]))))",
            "Enabled": true,
            "ID": "c8ec9537-7d43-4110-9600-650930b1e87f"
        },
        {
            "Command": "what is Johnny's order?",
            "Expected": [
                "salmon\nchicken\nWaiter: Can I get you anything besides a chicken and a salmon for Johnny?",
                "chicken\nsalmon\nWaiter: Can I get you anything besides a chicken and a salmon for Johnny?"
            ],
            "Tree": "which_q(x5,thing(x5),def_explicit_q(x3,proper_q(x10,named(Johnny,x10),[_order_n_of(x3), poss(e19,x3,x10)]),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "3e8edf8d-ab16-4c70-a35b-9976843a11e3"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "bf37523f-b62e-4a53-8da7-a2ac5462a9e3"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e41ae7cf-10ef-4454-ab98-d29c818cbfdd"
        },
        {
            "Command": "please get the chicken for me",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you?",
            "Tree": "_the_q(x10,pronoun_q(x16,pron(x16),[_chicken_n_1(x10), _for_p(e15,x10,x16)]),pronoun_q(x3,pron(x3),[polite(please,i5,e2), _get_v_1(e2,x3,x10)]))",
            "Enabled": true,
            "ID": "03b24006-18e9-4b63-ace8-025ebc9aef32"
        },
        {
            "Command": "get a steak for my son",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you and a steak for Johnny?",
            "Tree": "def_explicit_q(x14,pronoun_q(x20,pron(x20),[_son_n_of(x14,i25), poss(e19,x14,x20)]),pronoun_q(x3,pron(x3),_a_q(x8,[_steak_n_1(x8), _for_p(e13,x8,x14)],_get_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "99b1429b-cf55-4ca0-a26b-3748fcff3358"
        },
        {
            "Command": "My order is chicken",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides a chicken for you and a steak for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x14,_chicken_n_1(x14),def_explicit_q(x3,[_order_n_of(x3), poss(e8,x3,x9)],_be_v_id(e2,x3,x14))))",
            "Enabled": true,
            "ID": "a267e43b-17ce-4e94-a258-96cdf2e20b7a"
        },
        {
            "Command": "My son's order is steak",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides a chicken for you and a steak for Johnny?",
            "Tree": "pronoun_q(x10,pron(x10),def_explicit_q(x3,def_explicit_q(x5,[_son_n_of(x5,i15), poss(e9,x5,x10)],[_order_n_of(x3), poss(e20,x3,x5)]),udef_q(x21,_steak_n_1(x21),_be_v_id(e2,x3,x21))))",
            "Enabled": true,
            "ID": "9f85cd3c-3ef6-4776-a0eb-eea2c3704c39"
        },
        {
            "Command": "What did we order?",
            "Expected": [
                "steak\nchicken\nWaiter: Can I get you anything besides a chicken for you and a steak for Johnny?",
                "chicken\nsteak\nWaiter: Can I get you anything besides a chicken for you and a steak for Johnny?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e22dfd49-438f-46a2-98ad-30c4be9da431"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "c1694eb4-37db-44c1-828a-bfa8d9a60e42"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "3233ddfb-c919-4c18-bc9f-f76800860dac"
        },
        {
            "Command": "please bring us two glasses of water",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "pronoun_q(x11,pron(x11),udef_q(x10,udef_q(x22,_water_n_1(x22),[_glass_n_of(x10,x22), card(2,e21,x10)]),pronoun_q(x3,pron(x3),[polite(please,i5,e2), _bring_v_1(e2,x3,x10,x11)])))",
            "Enabled": true,
            "ID": "03b1227e-7481-45dd-afa0-e737b9d045cf"
        },
        {
            "Command": "what did I order?",
            "Expected": "water\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "3bea8a78-c76f-4a69-a18f-03f4fb55f13d"
        },
        {
            "Command": "what did Johnny order?",
            "Expected": "water\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "1b2a99a7-7850-49c0-8e91-93e7355f49c2"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "6a0783c0-04b9-4990-8653-98e906ba16b0"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "f2f7633a-d123-4e52-b0d6-af830a69a9b5"
        },
        {
            "Command": "Bring us 2 waters",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_water_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_bring_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "dfdd495d-5d82-49d9-bc95-bed3e6ebdf20"
        },
        {
            "Command": "what did I order?",
            "Expected": "water\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "50a55616-d99a-40dd-8a75-5328ff185b89"
        },
        {
            "Command": "what did Johnny order?",
            "Expected": "water\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "7d357afa-69a1-4002-a3a3-b224f8724807"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b406e76b-f802-4423-a953-fc8b9931a8e3"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "5e83ae9f-8377-430d-9ff6-4afd4325a537"
        },
        {
            "Command": "We'd like to start with some water and menus",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a water and a menu for you and a water and a menu for Johnny?",
            "Tree": "_some_q(x15,udef_q(x20,_water_n_1(x20),udef_q(x25,_menu_n_1(x25),_and_c(x15,x20,x25))),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "2ef6be00-e7ea-44a9-b73f-aea220402f94"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "menu\nwater\nWaiter: Can I get you anything besides a water and a menu for you and a water for Johnny?",
                "water\nmenu\nWaiter: Can I get you anything besides a water and a menu for you and a water for Johnny?",
                "water\nmenu\nWaiter: Can I get you anything besides a water and a menu for you and a water and a menu for Johnny?",
                "menu\nwater\nWaiter: Can I get you anything besides a water and a menu for you and a water and a menu for Johnny?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "c0f905da-c912-4070-9ed4-9e880e042617"
        },
        {
            "Command": "What did my son order?",
            "Expected": "menu\nwater\nWaiter: Can I get you anything besides a water and a menu for you and a water and a menu for Johnny?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "b076a0b6-5b3c-431c-afef-bb7a74b42df0"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2beacbb1-7cfc-40dd-9c08-cbfd6d3a1e32"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "82f05ce5-dc43-4d84-915d-0d2a6821eb25"
        },
        {
            "Command": "We'd like to start with some water",
            "Expected": "Waiter: water is an excellent choice!\nWaiter: Can I get you anything besides a water for you and a water for Johnny?",
            "Tree": "_some_q(x15,_water_n_1(x15),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "f99c7d3f-1ff8-4dc5-889c-e91860d64df0"
        },
        {
            "Command": "Can we have some menus?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a water and a menu for you and a water and a menu for Johnny?",
            "Tree": "_some_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "7a4b134b-3dcd-4290-a657-18dc3f2ed059"
        },
        {
            "Command": "I want some steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a water, a menu, and a steak for you and a water and a menu for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),_some_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4d11a206-7c07-42b2-91f5-6078d56e70dc"
        },
        {
            "Command": "how much is some soup?",
            "Expected": "4 dollars\nWaiter: Can I get you anything besides a water, a menu, and a steak for you and a water and a menu for Johnny?",
            "Tree": "which_q(x10,abstr_deg(x10),_some_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "e1240d1a-31dd-47cc-af00-bf2d0579b5c1"
        },
        {
            "Command": "I want some soups",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),_some_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1cb2c6e6-bab2-40d7-84b3-70f090e25a74"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "steak\n2 soup\nmenu\nwater\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "water\n2 soup\nmenu\nsteak\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "water\nsteak\nmenu\n2 soup\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "menu\n2 soup\nwater\nsteak\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "2 soup\nsteak\nwater\nmenu\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "2 soup\nwater\nsteak\nmenu\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "menu\nwater\n2 soup\nsteak\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "2 soup\nmenu\nsteak\nwater\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "water\nmenu\n2 soup\nsteak\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "steak\nmenu\n2 soup\nwater\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "2 soup\nwater\nmenu\nsteak\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "steak\nmenu\nwater\n2 soup\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "steak\n2 soup\nwater\nmenu\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "25fdf234-2ed3-435b-ab80-fb10e5389462"
        },
        {
            "Command": "What did my son order?",
            "Expected": [
                "water\nmenu\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?",
                "menu\nwater\nWaiter: Can I get you anything besides a water, a menu, a steak, and 2 soups for you and a water and a menu for Johnny?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x14,pron(x14),def_explicit_q(x3,[_son_n_of(x3,i19), poss(e13,x3,x14)],_order_v_1(e2,x3,x5))))",
            "Enabled": true,
            "ID": "daf4a340-1126-4f27-b87c-233dd8d3ba17"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "we'd like to start with a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x15,_table_n_1(x15),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "4a436537-1f34-4de5-8e2b-a4cb177c7605"
        },
        {
            "Command": "What did I order?",
            "Expected": "you ordered nothing\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e9ec6d48-008b-4c51-82e2-3f8d8b844b2c"
        },
        {
            "Command": "What did Johnny order?",
            "Expected": "Johnny ordered nothing\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),proper_q(x3,named(Johnny,x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "b202f65f-9778-4423-a925-395e1b0d8252"
        },
        {
            "Command": "What did we order?",
            "Expected": "you ordered nothing\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "8171037c-ba30-42bd-a9ce-ca63459df3c3"
        },
        {
            "Command": "I ordered a steak",
            "Expected": "a steak is not ordered.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "13ce708f-ec2a-41f8-b2dd-416711a3b810"
        },
        {
            "Command": "I can have a steak",
            "Expected": "I don't understand the way you are using: have\nWaiter: What can I get you?",
            "Tree": "_can_v_modal(e2,_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1(e10,x3,x11))))",
            "Enabled": true,
            "ID": "84e4fc9b-4d71-4538-8561-36449163906c"
        },
        {
            "Command": "Who can have a steak?",
            "Expected": "you\n(among others)\nWaiter: What can I get you?",
            "Tree": "which_q(x3,person(x3),_a_q(x11,_steak_n_1(x11),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "121251c1-efe2-47b5-a25f-a08648a34b5d"
        },
        {
            "Command": "What can I have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e15), _have_v_1_able(e2,x3,x5)]))",
            "Enabled": true,
            "ID": "9a9c9df7-aa60-4471-8afc-113bc4b32488"
        },
        {
            "Command": "I'd like to start with a steak and a soup",
            "Expected": "Waiter: steak is an excellent choice!\nSon: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything besides a menu and a steak for you?",
            "Tree": "udef_q(x15,_a_q(x20,_steak_n_1(x20),_a_q(x25,_soup_n_1(x25),_and_c(x15,x20,x25))),pronoun_q(x3,pron(x3),[_with_p(e14,e13,x15), event_replace(u99,e2,e13), _start_v_1_request(e2,x3)]))",
            "Enabled": true,
            "ID": "95ee387b-e08d-4263-b95e-a8f250546df3"
        },
        {
            "Command": "Can I have a steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "30071c2b-e13e-4ff0-9fa8-fea5b58b1873"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "2 steak\nmenu\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
                "menu\n2 steak\nWaiter: Can I get you anything besides a menu and 2 steaks for you?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e0b92b58-14c2-40f2-a985-d36a356ed8dd"
        },
        {
            "Command": "I ordered the steak",
            "Expected": "Yes, that is true.\n(there are more)\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "10f63f95-11f4-48d0-b722-94c8bc3e5d53"
        },
        {
            "Command": "I ordered 2 steaks",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e966e46f-9893-46de-a53c-efc026cafe28"
        },
        {
            "Command": "What did we order?",
            "Expected": "Host: Nothing.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "6e8ad609-7795-4d5c-96cd-cca160cf9f4e"
        },
        {
            "Command": "I will have a steak?",
            "Expected": "I don't understand the way you are using: have\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "73af9f66-e9d0-487a-9816-a582f7c3332f"
        },
        {
            "Command": "I will have a steak",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "76c09b78-40f9-4d01-ab0f-c7b9bd8946d9"
        },
        {
            "Command": "I will have a steak",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a319309e-f16c-48ee-8bfe-7d32324e1216"
        },
        {
            "Command": "I'll start with a steak",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 steak, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "_a_q(x9,_steak_n_1(x9),pronoun_q(x3,pron(x3),[_with_p(e8,e2,x9), _start_v_1(e2,x3)]))",
            "Enabled": true,
            "ID": "d0bd68b7-26e9-4575-ac55-49b7178169b1"
        },
        {
            "Command": "I will get the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_chicken_n_1(x8),_get_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "036118de-a9ab-429c-8d63-e65414a98b78"
        },
        {
            "Command": "I will have any meat",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_any_q(x8,_meat_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9a2a9945-3e16-4725-bf0a-b56918ade68a"
        },
        {
            "Command": "I'll take any meat dish",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "udef_q(x14,_meat_n_1(x14),pronoun_q(x3,pron(x3),_any_q(x8,[_dish_n_of(x8,i19), compound(e13,x8,x14)],_take_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a9bc7ac2-87d1-4d2d-b8f4-07b73c699cdd"
        },
        {
            "Command": "I will take the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_chicken_n_1(x8),_take_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "d8ca1c3b-7a12-4913-8427-67c51d28ecb0"
        },
        {
            "Command": "Cancel my order",
            "Expected": "Waiter: I have removed the order for you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x14,pron(x14),pronoun_q(x3,pron(x3),def_explicit_q(x8,[_order_n_of(x8), poss(e13,x8,x14)],_cancel_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "84adee7f-5273-4621-bc06-86b481ba54e5"
        },
        {
            "Command": "I want 2 steaks and 1 salad",
            "Expected": "Waiter: steak is an excellent choice!\nSon: Wait, let's not order salad before we know how much it costs.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "udef_q(x13,[_steak_n_1(x13), card(2,e18,x13)],udef_q(x20,[_salad_n_1(x20), card(1,e26,x20)],pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x20),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "5cf794bf-d096-4277-9de9-e1b0a1480e2c"
        },
        {
            "Command": "I ordered 2 steaks",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(2,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "20d71ea3-a742-4215-bbf2-4649fff8da3c"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "849d662d-f1dc-4ea8-9666-69b9f8e522aa"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "676c8863-4d33-4570-8141-145bbff1b417"
        },
        {
            "Command": "Let's go with two orders of the Steak, please",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_please_a_1(i23,udef_q(x11,_the_q(x18,_steak_n_1(x18),[_order_n_of(x11,x18), card(2,e17,x11)]),pronoun_q(x5,pron(x5),_want_v_1(e2,x5,x11))))",
            "Enabled": true,
            "ID": "be43e6b3-7a3f-4a03-8c31-9827b586a766"
        },
        {
            "Command": "Let's have the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_the_q(x9,_chicken_n_1(x9),pronoun_q(x5,pron(x5),_have_v_1(e2,x5,x9)))",
            "Enabled": true,
            "ID": "05db2218-cea5-4fcf-bd7d-25641a7261c8"
        },
        {
            "Command": "Let's go with the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_the_q(x10,_chicken_n_1(x10),pronoun_q(x5,pron(x5),_want_v_1(e2,x5,x10)))",
            "Enabled": true,
            "ID": "ba113d31-5097-4ab5-a93b-a48b2b26ccdd"
        },
        {
            "Command": "I want an order of the chicken",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 chicken, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_the_q(x13,_chicken_n_1(x13),pronoun_q(x3,pron(x3),_a_q(x8,_order_n_of(x8,x13),_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "a44c27d7-6a35-4828-9925-0da3ee1f6cf6"
        },
        {
            "Command": "What do the steak and the soup cost?",
            "Expected": "10 dollars\n4 dollars\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "which_q(x5,thing(x5),_the_q(x13,_steak_n_1(x13),_the_q(x18,_soup_n_1(x18),udef_q(x3,_and_c(x3,x13,x18),_cost_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "988a743e-3192-46a0-8d3c-e20eaf3cfb4d"
        },
        {
            "Command": "What will the steak cost?",
            "Expected": "10 dollars\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_steak_n_1(x3),_cost_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a723cb98-7894-4702-a56d-4850d0c8f5c4"
        },
        {
            "Command": "The steak costs 10 dollars",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_the_q(x3,_steak_n_1(x3),udef_q(x8,[_dollar_n_1(x8,u15), card(10,e14,x8)],_cost_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "983116b0-36a9-4950-9d75-616087bb9061"
        },
        {
            "Command": "What did the steak cost?",
            "Expected": "I don't understand the way you are using: cost\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "which_q(x5,thing(x5),_the_q(x3,_steak_n_1(x3),_cost_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e4de925b-11c5-4c07-b11a-4896e6d9fc69"
        },
        {
            "Command": "You will have a steak?",
            "Expected": "I don't understand the way you are using: have\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "37a62861-89f7-4aa7-ab60-7fbff5ad071d"
        },
        {
            "Command": "You will have a steak.",
            "Expected": "I'm not sure what that means.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "e80b2674-3527-4485-abc6-4368809ecb62"
        },
        {
            "Command": "What will I have?",
            "Expected": "Host: There isn't such a will, which I have here\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_which_q(x4,pronoun_q(x10,pron(x10),[_will_n_1(x4), _have_v_1(e14,x10,x4)]),unknown(e2,x4))",
            "Enabled": true,
            "ID": "a004ac87-0ab4-4ec1-bf9a-1d1940231aa8"
        },
        {
            "Command": "Who will have a steak?",
            "Expected": "I don't understand the way you are using: have\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "which_q(x3,person(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "74aa2bec-f3d0-457a-98f0-afbbd59e9f88"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4919a6c6-a36d-4c96-83fc-199d289eeb11"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4f7dd64f-df78-46b5-8700-3b4e2c5097f5"
        },
        {
            "Command": "What are the specials?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_the_q(x8,_special_n_1(x8),_be_v_id(e2,x3,x8)))",
            "Enabled": true,
            "ID": "169a1146-bc00-4e1c-936c-cc2b903e3f46"
        },
        {
            "Command": "What specials do you have?",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,_special_n_1(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "98667127-8757-4b90-9e2a-b4484844ad29"
        },
        {
            "Command": "What are your specials?",
            "Expected": "soup\nsalad\npork\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "d122cc5c-a482-4b45-9345-0681627b6589"
        },
        {
            "Command": "Which dishes are specials?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "_which_q(x5,_dish_n_of(x5,i9),udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "a8713a17-5c05-4028-8c03-1602d9c014f0"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "02b1c558-1064-4bd4-9fa3-afb3828ff5f7"
        },
        {
            "Command": "Which two dishes are specials?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i11), card(2,e10,x5)],udef_q(x3,_special_n_1(x3),_be_v_id(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e8e03861-59c8-4f05-b5db-c88d3646a572"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "c2877f26-4c57-48b8-8e5f-f7809e671537"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "3683bdd4-f7e4-419c-bc16-f5df21f5cc41"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b4d472d4-4e03-4787-9360-8cf5a2920847"
        },
        {
            "Command": "I want a salad",
            "Expected": "Son: Wait, let's not order salad before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ee8d866-b726-444f-9abd-ba2db97f8caf"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a steak for you?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2e558271-ef87-41e2-a5ba-d67ea0b5e4a3"
        },
        {
            "Command": "I'd like a steak'",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ac9ca7b7-60b3-4d02-8b03-9fa62fb80095"
        },
        {
            "Command": "My son would like a salmon",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x18,_salmon_n_1(x18),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x18))))",
            "Enabled": true,
            "ID": "603ebce5-dcab-45a3-abdd-df45f4106a1b"
        },
        {
            "Command": "Johnny would love the salmon",
            "Expected": "Son: Wait, we already spent $20 so if we get 1 salmon, we won't be able to pay for it with $20.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "_the_q(x12,_salmon_n_1(x12),proper_q(x3,named(Johnny,x3),_want_v_1(e2,x3,x12)))",
            "Enabled": true,
            "ID": "99d72ecb-d330-4bc9-bc81-17c870cf26c8"
        },
        {
            "Command": "Can we get one soup for Johnny, please?",
            "Expected": "Son: Wait, let's not order soup before we know how much it costs.\nWaiter: Can I get you anything besides 2 steaks for you?",
            "Tree": "udef_q(x11,proper_q(x19,named(Johnny,x19),[_soup_n_1(x11), _for_p(e18,x11,x19), card(1,e17,x11)]),pronoun_q(x3,pron(x3),[_please_a_1(e25,e10), event_replace(u99,e2,e10), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "b3589252-e0bf-4534-8bfa-c2d079bc4700"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "db0eb32b-5205-40e8-a821-35975d4668b5"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "8d7e82ba-9d89-46b2-8532-8ca326bea794"
        },
        {
            "Command": "We'll have one tomato soup and one green salad, please.",
            "Expected": "Son: Wait, let's not order soup before we know how much it costs.\nSon: Wait, let's not order salad before we know how much it costs.\nWaiter: What can I get you?",
            "Tree": "udef_q(x13,udef_q(x20,_tomato_n_1(x20),[_soup_n_1(x13), compound(e19,x13,x20), card(1,e18,x13)]),udef_q(x26,[_salad_n_1(x26), _green_a_2(e33,x26), card(1,e32,x26)],pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x26),[_please_a_1(e34,e2), _have_v_1(e2,x3,x8)]))))",
            "Enabled": true,
            "ID": "c06eb8ef-1e74-42dd-b82c-a1a02c54ec08"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "97832479-2a91-409f-a087-01583cf1e068"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "a20ee8de-8e51-4482-9732-b55e2081b7d6"
        },
        {
            "Command": "I would like the salmon",
            "Expected": "Waiter: salmon is an excellent choice!\nWaiter: Can I get you anything besides a salmon for you?",
            "Tree": "_the_q(x11,_salmon_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "3003a1eb-14b6-4dfe-9fe9-496d3a3e44a1"
        },
        {
            "Command": "What did I order?",
            "Expected": "salmon\nWaiter: Can I get you anything besides a salmon for you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "cbe31443-8b30-48e9-a530-a131548fa6b5"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2ba0af2c-9d36-4c23-abc3-9112283310d7"
        },
        {
            "Command": "we'd like a table for 2'",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,number_q(x17,card(2,x17,i23),[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5463c147-27e5-4920-934b-c6bfddc3741c"
        },
        {
            "Command": "How much is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "0c66d40d-000d-4f44-b15b-ec79e5bd018a"
        },
        {
            "Command": "How many dollars is the soup?",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x9,abstr_deg(x9),_the_q(x3,_soup_n_1(x3),count(e14,x9,x5,udef_q(x5,_dollar_n_1(x5,u16),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "bf8680e8-0acf-42da-93c5-defa879f7f10"
        },
        {
            "Command": "How much is the salad?",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "5d7616ff-0fe6-482a-a57b-67ea07f9cf72"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "b4244624-885e-478c-9b76-7d2105388a57"
        },
        {
            "Command": "How much are the dishes?",
            "Expected": "10 dollars\n7 dollars\n12 dollars\n8 dollars\n4 dollars\n3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_dish_n_of(x3,i20),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "ae8dcc8e-316b-4754-8b00-81078a5f2c4b"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "a28bfe6b-38b2-42e3-9726-52fe0bf3909d"
        },
        {
            "Command": "I would like the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for you?",
            "Tree": "_the_q(x11,_salad_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "7a84fe83-a358-4884-932d-cf00e69eb5bb"
        },
        {
            "Command": "I would like the soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a salad and a soup for you?",
            "Tree": "_the_q(x11,_soup_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ad7a56d1-f75d-4cef-9649-99aa5aaae31d"
        },
        {
            "Command": "What did I order?",
            "Expected": [
                "soup\nsalad\nWaiter: Can I get you anything besides a salad and a soup for you?",
                "salad\nsoup\nWaiter: Can I get you anything besides a salad and a soup for you?"
            ],
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "f04f7d4e-c918-4d46-81f0-a4bf4044dae4"
        },
        {
            "Command": "I ordered salad and soup",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides a salad and a soup for you?",
            "Tree": "udef_q(x13,_salad_n_1(x13),udef_q(x18,_soup_n_1(x18),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x18),_order_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "bd6b1750-5480-4661-a1d6-600bb7dbbc2a"
        },
        {
            "Command": "I ordered the soup",
            "Expected": "Yes, that is true.\nWaiter: Can I get you anything besides a salad and a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "c3b2b4ed-9938-468a-8567-250e7833d15f"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "aba36868-59d9-48ab-bff0-123bf1d37386"
        },
        {
            "Command": "How much are the dishes?",
            "Expected": "10 dollars\n7 dollars\n12 dollars\n8 dollars\n4 dollars\n3 dollars\nWaiter: Can I get you anything besides a salad and a soup for you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_dish_n_of(x3,i20),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "e13e91ec-7395-4c36-a509-3296ec3d427c"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "e98f4773-fb13-45aa-8275-78b24b1c16fb"
        },
        {
            "Command": "How much are the specials?",
            "Expected": "4 dollars\n3 dollars\n8 dollars\nWaiter: Can I get you anything besides a salad and a soup for you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_special_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "ca595830-25f1-4b1b-a74e-3d47e4515acd"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "2724f690-0b1e-47ab-823a-d712c996622c"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "34976bba-3203-4639-a0eb-68903a90ca33"
        },
        {
            "Command": "How much do the specials cost?",
            "Expected": "4 dollars\n3 dollars\n8 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_special_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_cost_v_1(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "6085ec6b-9636-47db-bb63-03192fe8605f"
        },
        {
            "Command": "I want soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "888ee475-5cac-4f92-87b5-8a04d7b0fed0"
        },
        {
            "Command": "I want salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a soup and a salad for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "6f10abe3-2b46-47fc-8fec-63bccadb36bb"
        },
        {
            "Command": "I want pork",
            "Expected": "Waiter: pork is an excellent choice!\nWaiter: Can I get you anything besides a soup, a salad, and a pork for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_pork_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "59a2e11f-c5cd-4613-9628-7ffb6d53cee2"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "24b825d2-634c-43c8-97f9-038a5fbb2829"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "bf163c10-e572-44eb-b403-6d2ef7a2073b"
        },
        {
            "Command": "I want 3 steaks",
            "Expected": "Son: Wait, we already spent $0 so if we get 3 steak, we won't be able to pay for it with $20.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(3,e14,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f412ffe0-207b-4b36-b8a4-b4e541ff3817"
        },
        {
            "Command": "what did I order",
            "Expected": "you ordered nothing\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_order_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "18d4ddaa-a0b5-4c6e-be76-f52dc41dda77"
        },
        {
            "Command": "I ordered 3 steaks",
            "Expected": "3 steak are not ordered.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_steak_n_1(x8), card(3,e14,x8)],_order_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "326fcaba-7595-4143-9309-9142c06b5607"
        },
        {
            "Command": "/timeout",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "29f7481f-d6de-4e6d-a96d-b253cdc300b3"
        },
        {
            "Command": "soup and salad are vegetarian dishes",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "udef_q(x13,_salad_n_1(x13),udef_q(x18,[_dish_n_of(x18,i24), _vegetarian_a_1(e23,x18)],udef_q(x3,udef_q(x8,_soup_n_1(x8),_and_c(x3,x8,x13)),_be_v_id(e2,x3,x18))))",
            "Enabled": true,
            "ID": "a294ee3b-dfbd-4801-a01f-1b5ad96f4ff3"
        },
        {
            "Command": "/timeout 15",
            "Expected": "",
            "Tree": "",
            "Enabled": true,
            "ID": "d2cc5ff0-91ef-4b7a-887a-29cb8adac9a5"
        }
    ],
    "ElapsedTime": 538.4753
}