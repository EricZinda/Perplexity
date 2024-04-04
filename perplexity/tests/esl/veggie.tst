{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "5f6ab01b-f45d-45e0-80e5-2f73e4387ece"
        },
        {
            "Command": "which vegetarian items do you have?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_item_n_of(x5,i10), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "e0096011-560c-4806-b093-402709a8419b"
        },
        {
            "Command": "which vegetarian menu items do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,udef_q(x11,_menu_n_1(x11),[_item_n_of(x5,i16), compound(e10,x5,x11), _vegetarian_a_1(e9,x5)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "37e73c8f-ea36-4f95-8afc-7efa06823a41"
        },
        {
            "Command": "which vegetarian specialities do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_speciality_n_1(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "279ea601-fe4b-4d46-a24d-33334fc63dfb"
        },
        {
            "Command": "which vegetarian menu choices do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,udef_q(x11,_menu_n_1(x11),[_choice_n_of(x5,i16), compound(e10,x5,x11), _vegetarian_a_1(e9,x5)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "bad3cea5-19d2-4c65-868d-a95e425861f6"
        },
        {
            "Command": "which vegetarian mains do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_main_n_1(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "b1cad5fa-263e-4a4d-964a-ed03d45e98a6"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ec9b6dbe-ebe8-4134-a339-3c43e92eb86e"
        },
        {
            "Command": "is the soup vegetarian?",
            "Expected": "Yes.",
            "Tree": "_the_q(x3,_soup_n_1(x3),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "a4264b95-47fb-4468-89f4-adfc0e27dcf2"
        },
        {
            "Command": "is the soup not vegetarian?",
            "Expected": "That isn't true, there isn't the soup that isn't the vegetarian soup",
            "Tree": "neg(e8,_the_q(x3,_soup_n_1(x3),_vegetarian_a_1(e2,x3)))",
            "Enabled": false,
            "ID": "26fc6f0a-7692-4135-8859-c27a1b3e9129"
        }
    ],
    "ElapsedTime": 3.1912
}