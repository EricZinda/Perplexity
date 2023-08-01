{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "seat me",
            "Expected": "How many in your party?",
            "Tree": "pronoun_q(x8,pron(x8),pronoun_q(x3,pron(x3),_seat_v_cause(e2,x3,x8)))",
            "Enabled": true,
            "ID": "af81b14e-44fb-4f87-b8bb-8f01f09352f5"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "udef_q(x4,[generic_entity(x4), card(2,e10,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "1e36dc11-2a7d-440e-9274-09c1b25561ea"
        },
        {
            "Command": "what do you have?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "bf7013bd-b519-4bee-9b6f-d600274426f1"
        },
        {
            "Command": "can I see the menu?",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "d86c1b84-85f6-4f94-980e-e5b05874cf4a"
        },
        {
            "Command": "i want a steak",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "69fa7f66-914d-41d8-b3ec-beb74c2a7c6c"
        },
        {
            "Command": "I want a steak",
            "Expected": "Son: Wait, we already spent $10 so if we get that, we won't be able to pay for it with $15. \nWaiter: Can I get you something else before I put your order in?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9dee827f-8ad6-451d-96d4-c12b68b94264"
        },
        {
            "Command": "no",
            "Expected": "Son: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu\u2026 You tell the waiter to restart your order.\nWaiter: Ok, can I get you something else to eat?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "0b5e5bbd-48b0-4ebc-b51f-ca99f2023846"
        },
        {
            "Command": "what vegetarian dishes do you have?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and porkchops.",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "4bb9d864-d8bd-47da-b1ff-707b78fa81af"
        },
        {
            "Command": "how much is the soup?",
            "Expected": "4 dollars",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_soup_n_1(x3),udef_q(x5,[measure(e14,e15,x10), generic_entity(x5), much-many_a(e15,x5)],_be_v_id(e2,x3,x5))))",
            "Enabled": true,
            "ID": "da4852a3-7b16-4669-8cef-8c0c6b05ce91"
        },
        {
            "Command": "i want the soup",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_soup_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a988a546-6826-4dd8-848d-2c119ed7dd68"
        },
        {
            "Command": "the steak",
            "Expected": "Excellent Choice! Can I get you anything else?",
            "Tree": "_the_q(x4,_steak_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "09d6f18e-f3b2-4f22-ae96-bc9b6f500626"
        },
        {
            "Command": "no",
            "Expected": "Ok, I'll be right back with your meal.\nA few minutes go by and the robot returns with soup0 steak0.\nThe food is good, but nothing extraordinary.",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "ddb7c01a-a8c1-42af-9776-ffc933cb69d9"
        },
        {
            "Command": "check, please",
            "Expected": "Your total is 14 dollars. Would you like to pay by cash or card?",
            "Tree": "pronoun_q(x3,pron(x3),[_please_a_1(e9,e2), _check_v_1(e2,x3,i8)])",
            "Enabled": true,
            "ID": "1108248a-eb0f-42cf-88d3-c93baa41a049"
        },
        {
            "Command": "cash",
            "Expected": "Ah. Perfect! Have a great rest of your day.(there are more)",
            "Tree": "udef_q(x4,_cash_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "1b243ee9-08a0-4942-bc6f-d09ddd2e1856"
        }
    ]
}