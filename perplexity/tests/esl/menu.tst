{
    "ResetModule": "tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d32088e1-b1c1-406e-a849-c6b13efef46d"
        },
        {
            "Command": "I want a vegetarian menu",
            "Expected": "Host: There isn't such a vegetarian menu here",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _vegetarian_a_1(e13,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "Can I see a menu?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_see_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "ed0e789c-6ba1-4e91-98fd-a9bea2f02e27"
        },
        {
            "Command": "Do you have a menu?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9a11bb68-b6a7-4ae5-87da-ce2853e821a9"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "22a6851e-3314-4bc9-8067-ed352aceb570"
        },
        {
            "Command": "We will see a menu",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8fd795d7-6127-4186-b87b-67680e2c551e"
        },
        {
            "Command": "Could we have a menu?",
            "Expected": "Sorry, you must be seated to get a menu",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_have_v_1_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "4a0fe26c-88b6-4386-8e7b-af607075c4f6"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "43819cbc-f246-4e69-ba81-87f2f743e348"
        },
        {
            "Command": "I want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "9de52751-9c4b-4640-ab7f-6a53f5aff66d"
        },
        {
            "Command": "Do you have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "976df396-5503-40d5-90fe-93f121237afe"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "0f81d780-5bdb-4976-aae2-6144f9c6b89b"
        },
        {
            "Command": "do you have a steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "93451d18-612d-427f-bb67-ccea34c7aa58"
        },
        {
            "Command": "do you have the steak?",
            "Expected": "Yes.",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ed01aa0e-79b0-4c3d-8443-f9bac852a7d4"
        },
        {
            "Command": "show me the menu",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x8,_menu_n_1(x8),pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "3abc1ec5-890e-4d20-83fd-58479d75bf6a"
        },
        {
            "Command": "show me 2 menus",
            "Expected": "Waiter: Our policy is to give one menu to every customer ...",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "cde58b5d-7df0-4173-a792-d2379fdf4716"
        },
        {
            "Command": "show us 2 menus",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "94dafbfe-00ea-4830-ab9b-e3069733741c"
        },
        {
            "Command": "show us 3 menus",
            "Expected": "That seems like an excessive number of menus ...\n",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(3,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "988f2dbf-fc14-4a2a-a108-62a105abb9cb"
        },
        {
            "Command": "we have 2 menus",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(2,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4dd1ccc3-2b8d-4c5e-8048-cfef07a8d1d4"
        },
        {
            "Command": "we have 3 menus",
            "Expected": "There are less than 3 3 menu",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(3,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "28216fc8-69b6-40cb-a699-27c8460b77f9"
        },
        {
            "Command": "can you seat me?",
            "Expected": "Um... You're at a table.",
            "Tree": "pronoun_q(x11,pron(x11),pronoun_q(x3,pron(x3),_seat_v_cause_able(e2,x3,x11)))",
            "Enabled": true,
            "ID": "5e54a63a-49e8-444f-9b6f-b50555f6f63c"
        },
        {
            "Command": "2",
            "Expected": "Sorry, we don't allow ordering specific things like that",
            "Tree": "number_q(x4,card(2,x4,i10),unknown(e2,x4))",
            "Enabled": true,
            "ID": "9dd7913d-e27e-4750-9204-6dc50b87c258"
        },
        {
            "Command": "can you show me the menu?",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "21e7c526-6227-4537-be14-54a95bff30e7"
        },
        {
            "Command": "could you show me the menu?",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "60bcfe97-9570-45f5-a87e-2abf2eb0136c"
        },
        {
            "Command": "what vegetarian dishes are there?",
            "Expected": "Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],_be_v_there(e2,x5))",
            "Enabled": true,
            "ID": "a62bdeda-54d0-4517-9e33-c5925a4bd1ed"
        }
    ]
}