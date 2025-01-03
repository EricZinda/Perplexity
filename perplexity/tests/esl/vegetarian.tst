{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "5f6ab01b-f45d-45e0-80e5-2f73e4387ece"
        },
        {
            "Command": "salad is vegetarian",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "udef_q(x3,_salad_n_1(x3),_vegetarian_a_1(e2,x3))",
            "Enabled": true,
            "ID": "e0096011-560c-4806-b093-402709a8419b"
        },
        {
            "Command": "salmon and steak and salad are not vegetarian",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "neg(e28,udef_q(x12,_salmon_n_1(x12),udef_q(x17,_steak_n_1(x17),udef_q(x23,_salad_n_1(x23),udef_q(x3,udef_q(x8,_and_c(x8,x12,x17),_and_c(x3,x8,x23)),_vegetarian_a_1(e2,x3))))))",
            "Enabled": true,
            "ID": "8fcc1b7f-8728-43a8-92e3-c6a44a2bd360"
        },
        {
            "Command": "soup, salad and steak are vegetarian",
            "Expected": "soup, salad, and steak are not vegetarian\nWaiter: What can I get you?",
            "Tree": "udef_q(x13,udef_q(x18,_salad_n_1(x18),udef_q(x23,_steak_n_1(x23),_and_c(x13,x18,x23))),udef_q(x3,udef_q(x8,_soup_n_1(x8),implicit_conj(x3,x8,x13)),_vegetarian_a_1(e2,x3)))",
            "Enabled": true,
            "ID": "4aee1a8f-7e50-461a-9448-c7e055b142de"
        },
        {
            "Command": "salmon, pork and steak are not vegetarian",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "neg(e28,udef_q(x13,udef_q(x18,_pork_n_1(x18),udef_q(x23,_steak_n_1(x23),_and_c(x13,x18,x23))),udef_q(x3,udef_q(x8,_salmon_n_1(x8),implicit_conj(x3,x8,x13)),_vegetarian_a_1(e2,x3))))",
            "Enabled": true,
            "ID": "945f1d11-fa30-46a6-ac2f-ef1f2ec325c8"
        },
        {
            "Command": "soup and soup and salad are vegetarian",
            "Expected": "Yes, that is true.\n(there are more)\nWaiter: What can I get you?",
            "Tree": "udef_q(x12,_soup_n_1(x12),udef_q(x17,_soup_n_1(x17),udef_q(x23,_salad_n_1(x23),udef_q(x3,udef_q(x8,_and_c(x8,x12,x17),_and_c(x3,x8,x23)),_vegetarian_a_1(e2,x3)))))",
            "Enabled": true,
            "ID": "291a1146-c4a8-4253-8dda-a9e1a83c59df"
        },
        {
            "Command": "vegetarian",
            "Expected": "Host: Sorry, I'm not sure which one you mean.\nWaiter: What can I get you?",
            "Tree": "udef_q(x4,_vegetarian_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "d5b42217-827a-4c43-8200-5f8bd6192cff"
        },
        {
            "Command": "which vegetarian items do you have?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_thing_n_of-about(x5,i10), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "39b66454-0d3b-4ae0-8a16-64d9f2d32922"
        },
        {
            "Command": "which vegetarian menu items do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,udef_q(x11,_menu_n_1(x11),[_thing_n_of-about(x5,i16), compound(e10,x5,x11), _vegetarian_a_1(e9,x5)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "37e73c8f-ea36-4f95-8afc-7efa06823a41"
        },
        {
            "Command": "Do you have any vegetarian menu items?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "udef_q(x15,_menu_n_1(x15),pronoun_q(x3,pron(x3),_any_q(x8,[_thing_n_of-about(x8,i20), compound(e14,x8,x15), _vegetarian_a_1(e13,x8)],_have_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "752fedfb-9214-4995-835a-586ad105e629"
        },
        {
            "Command": "which vegetarian specialities do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "279ea601-fe4b-4d46-a24d-33334fc63dfb"
        },
        {
            "Command": "which vegetarian menu choices do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,udef_q(x11,_menu_n_1(x11),[_dish_n_of(x5,i16), compound(e10,x5,x11), _vegetarian_a_1(e9,x5)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "bad3cea5-19d2-4c65-868d-a95e425861f6"
        },
        {
            "Command": "which vegetarian mains do you have?",
            "Expected": "soup\nsalad\nWaiter: What can I get you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5), _vegetarian_a_1(e9,x5)],pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "b1cad5fa-263e-4a4d-964a-ed03d45e98a6"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "ec9b6dbe-ebe8-4134-a339-3c43e92eb86e"
        },
        {
            "Command": "is the soup vegetarian?",
            "Expected": "Yes.\nHost: How can I help you today?",
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
    "ElapsedTime": 19.19725
}