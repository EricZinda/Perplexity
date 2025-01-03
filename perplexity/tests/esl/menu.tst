{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "05cf91e2-b1d4-4dc6-82b2-8614bd04382b"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "e3ce792d-b076-4fc4-b91d-7e13976d58f6"
        },
        {
            "Command": "Could we have a vegetarian menu?",
            "Expected": "Host: There isn't such a vegetarian menu here\nWaiter: What can I get you?",
            "Tree": "_a_q(x11,[_menu_n_1(x11), _vegetarian_a_1(e16,x11)],pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "bc1ce7b9-3611-48fa-9baf-5288edde5c55"
        },
        {
            "Command": "I want a menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b500d164-d028-4510-9938-18d6fd2bf267"
        },
        {
            "Command": "I want to eat lunch",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "udef_q(x11,_dish_n_of(x11),pronoun_q(x3,pron(x3),_eat_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "db7bdc29-02fb-41fb-a0a8-269f2c0da6d7"
        },
        {
            "Command": "we want to eat lunch",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "udef_q(x11,_dish_n_of(x11),pronoun_q(x3,pron(x3),_eat_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "35de31fb-bf6d-425d-935b-b1c23e999c7a"
        },
        {
            "Command": "We'd both like a menu",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "_a_q(x12,_menu_n_1(x12),pronoun_q(x3,pron(x3),[_both_a_1(i9,e2), _want_v_1(e2,x3,x12)]))",
            "Enabled": true,
            "ID": "d30b2343-955a-4d2f-ade5-736c1cf2ff73"
        },
        {
            "Command": "I want one menu for me and one menu for johnny",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "udef_q(x13,pronoun_q(x20,pron(x20),[_menu_n_1(x13), _for_p(e19,x13,x20), card(1,e18,x13)]),udef_q(x26,proper_q(x34,named(Johnny,x34),[_menu_n_1(x26), _for_p(e33,x26,x34), card(1,e32,x26)]),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x26),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "67d18d03-becc-4804-97bf-69579afc2caa"
        },
        {
            "Command": "I want one menu for me and two menus for johnny",
            "Expected": "Waiter: Our policy is to give one menu to every customer ...\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "udef_q(x13,pronoun_q(x20,pron(x20),[_menu_n_1(x13), _for_p(e19,x13,x20), card(1,e18,x13)]),udef_q(x26,proper_q(x34,named(Johnny,x34),[_menu_n_1(x26), _for_p(e33,x26,x34), card(2,e32,x26)]),pronoun_q(x3,pron(x3),udef_q(x8,_and_c(x8,x13,x26),_want_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "29c11ecb-431c-4fd3-b465-178433d09b48"
        },
        {
            "Command": "that will be all",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a menu for you.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "no_standalone(e2)",
            "Enabled": true,
            "ID": "4ee29d7a-4ec4-45ae-be8e-d0735a4718c2"
        },
        {
            "Command": "ok.",
            "Expected": "\nWaiter: What can I get you?",
            "Tree": "_okay_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "2ba8f361-0a88-48e9-b7fe-d65d53b8f399"
        },
        {
            "Command": "Do you have lunch?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_dish_n_of(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ecab638-357a-43e6-b768-421b52437bdb"
        },
        {
            "Command": "We'd like to get lunch",
            "Expected": "Waiter: Oh, I already gave you a menu. You can see that there is a menu in front of you.\nWaiter: Oh, I already gave Johnny a menu. You can see that there is a menu in front of Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "udef_q(x14,_dish_n_of(x14),pronoun_q(x3,pron(x3),_get_v_1_request(e13,x3,x14)))",
            "Enabled": true,
            "ID": "5c5c0922-48a6-4624-86f1-c8c208447029"
        },
        {
            "Command": "I would like to get some lunch",
            "Expected": "Waiter: Oh, I already gave you a menu. You can see that there is a menu in front of you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_some_q(x14,_dish_n_of(x14),pronoun_q(x3,pron(x3),_get_v_1_request(e13,x3,x14)))",
            "Enabled": true,
            "ID": "bcded24c-1553-41a5-8d2c-8a4ed64e7593"
        },
        {
            "Command": "I would like to order lunch",
            "Expected": "Waiter: Oh, I already gave you a menu. You can see that there is a menu in front of you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "udef_q(x14,_dish_n_of(x14),pronoun_q(x3,pron(x3),_order_v_1_request(e13,x3,x14)))",
            "Enabled": true,
            "ID": "bef48dc6-b626-4c92-9214-e8e73dda9ff1"
        },
        {
            "Command": "Could we have lunch?",
            "Expected": "Waiter: Oh, I already gave you a menu. You can see that there is a menu in front of you.\nWaiter: Oh, I already gave Johnny a menu. You can see that there is a menu in front of Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,_dish_n_of(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "c58523c4-4d4b-48e1-a384-5e0f76db6166"
        },
        {
            "Command": "My son wants the menu",
            "Expected": "Waiter: Oh, I already gave Johnny a menu. You can see that there is a menu in front of Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "8f673224-8186-4d58-8b0f-2c285ec4891c"
        },
        {
            "Command": "that will be all, thank you.",
            "Expected": "You realize that you'll need at least two dishes for the two of you.\nYou are welcome!\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x16,pron(x16),[no_standalone(e9)])<end>pronoun_q(x16,pron(x16),[_thank_v_1(e10,x5,x16)])",
            "Enabled": true,
            "ID": "3eb18b1a-240f-4fea-957b-4e9c98bcbdce"
        },
        {
            "Command": "We would like the menus",
            "Expected": "There are less than 2 menu\nWaiter: What can I get you?",
            "Tree": "_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "42d5f855-1b6d-4b48-9f8f-edecceec3774"
        },
        {
            "Command": "What is on the menu?",
            "Expected": "salmon\nsteak\nchicken\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),_the_q(x8,_menu_n_1(x8),_on_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "cd3a359d-3058-4020-8b8e-58b7f48fea10"
        },
        {
            "Command": "Chicken is on the menu.",
            "Expected": "Yes, that is true.\nWaiter: What can I get you?",
            "Tree": "udef_q(x3,_chicken_n_1(x3),_the_q(x8,_menu_n_1(x8),_on_p_loc(e2,x3,x8)))",
            "Enabled": true,
            "ID": "68e059af-f4de-4cb0-8f40-20908b6d6048"
        },
        {
            "Command": "Is anything vegetarian on the menu?",
            "Expected": "Yes.\nWaiter: What can I get you?",
            "Tree": "_the_q(x9,_menu_n_1(x9),_any_q(x3,[thing(x3), _vegetarian_a_1(e8,x3)],_on_p_loc(e2,x3,x9)))",
            "Enabled": true,
            "ID": "9a1dc895-a294-4baa-a3b2-377bdd094bb0"
        },
        {
            "Command": "What vegetarian items are on the menu?",
            "Expected": "vegetarian thing\nWaiter: What can I get you?",
            "Tree": "_which_q(x3,[_thing_n_of-about(x3,i9), _vegetarian_a_1(e8,x3)],_the_q(x10,_menu_n_1(x10),_on_p_loc(e2,x3,x10)))",
            "Enabled": true,
            "ID": "a7c93ebb-42c4-4c95-ba47-072e452348a2"
        },
        {
            "Command": "What isn't on the menu?",
            "Expected": "tomato\nbill\ncheck\nson\nroast\nWaiter: What can I get you?",
            "Tree": "which_q(x3,thing(x3),neg(e2,_the_q(x11,_menu_n_1(x11),_on_p_loc(e10,x3,x11))))",
            "Enabled": true,
            "ID": "4bf6c98e-0bb4-43b8-9652-e5054b58e1ad"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d32088e1-b1c1-406e-a849-c6b13efef46d"
        },
        {
            "Command": "I want a vegetarian menu",
            "Expected": "I'm not sure which vegetarian menu you mean.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _vegetarian_a_1(e13,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "Can I see a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _see_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "ed0e789c-6ba1-4e91-98fd-a9bea2f02e27"
        },
        {
            "Command": "Do you have a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9a11bb68-b6a7-4ae5-87da-ce2853e821a9"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "22a6851e-3314-4bc9-8067-ed352aceb570"
        },
        {
            "Command": "We will see a menu",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8fd795d7-6127-4186-b87b-67680e2c551e"
        },
        {
            "Command": "Could we have a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "9de52751-9c4b-4640-ab7f-6a53f5aff66d"
        },
        {
            "Command": "Do you have a menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "976df396-5503-40d5-90fe-93f121237afe"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "0f81d780-5bdb-4976-aae2-6144f9c6b89b"
        },
        {
            "Command": "do you have a steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a menu and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "93451d18-612d-427f-bb67-ccea34c7aa58"
        },
        {
            "Command": "do you have the steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ed01aa0e-79b0-4c3d-8443-f9bac852a7d4"
        },
        {
            "Command": "which chicken menu items do you have?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "_which_q(x5,udef_q(x10,udef_q(x16,_chicken_n_1(x16),[_menu_n_1(x10), compound(e15,x10,x16)]),[_thing_n_of-about(x5,i21), compound(e9,x5,x10)]),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": false,
            "ID": "3abc1ec5-890e-4d20-83fd-58479d75bf6a"
        },
        {
            "Command": "show me the menu",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x8,_menu_n_1(x8),pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "37589356-dc72-4d63-a595-4792436fa15a"
        },
        {
            "Command": "show me 2 menus",
            "Expected": "Waiter: Our policy is to give one menu to every customer ...\nWaiter: Can I get you anything besides a menu and 2 steaks for you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "cde58b5d-7df0-4173-a792-d2379fdf4716"
        },
        {
            "Command": "show us 2 menus",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a menu and 2 steaks for you and a menu for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "94dafbfe-00ea-4830-ab9b-e3069733741c"
        },
        {
            "Command": "could we see menus?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a menu and 2 steaks for you and a menu for Johnny?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _see_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "ec1ad85b-ce21-4f93-a7e7-c67a616fb8e8"
        },
        {
            "Command": "that will be all, thanks",
            "Expected": "Johnny: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu? \nYou tell the waiter to ignore what you just ordered.\nWaiter: What can I get you?",
            "Tree": "_thanks_a_1(i15,no_standalone(e2))",
            "Enabled": true,
            "ID": "4e977eb7-06e3-42e4-9c00-a7ad22602325"
        },
        {
            "Command": "which chicken menu item do you have?",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you?",
            "Tree": "_which_q(x5,udef_q(x10,_chicken_n_1(x10),udef_q(x16,_menu_n_1(x16),[_thing_n_of-about(x5,i21), compound(e15,x5,x16), compound(e9,x5,x10)])),pronoun_q(x3,pron(x3),_have_v_1(e2,x3,x5)))",
            "Enabled": true,
            "ID": "d13bf1c4-5a27-467c-85c1-e6eb7219b82d"
        },
        {
            "Command": "cancel my chicken order",
            "Expected": "Waiter: I have removed a chicken from the order for you.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x14,pron(x14),udef_q(x20,_chicken_n_1(x20),pronoun_q(x3,pron(x3),def_explicit_q(x8,[_order_n_of(x8), compound(e19,x8,x20), poss(e13,x8,x14)],_cancel_v_1(e2,x3,x8)))))",
            "Enabled": true,
            "ID": "988f2dbf-fc14-4a2a-a108-62a105abb9cb"
        },
        {
            "Command": "show us 3 menus",
            "Expected": "Waiter: Our policy is to give one menu to every customer ...\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(3,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "da521971-c648-4870-a4a1-dc25d2f1baf6"
        },
        {
            "Command": "we have 2 menus",
            "Expected": "you do not have 2 menu\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(2,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4dd1ccc3-2b8d-4c5e-8048-cfef07a8d1d4"
        },
        {
            "Command": "we have 3 menus",
            "Expected": "you do not have 3 menu\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(3,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "28216fc8-69b6-40cb-a699-27c8460b77f9"
        },
        {
            "Command": "can you seat me?",
            "Expected": "Waiter: Um... You're at a table.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x11,pron(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _seat_v_cause_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "5e54a63a-49e8-444f-9b6f-b50555f6f63c"
        },
        {
            "Command": "2",
            "Expected": "Waiter: Sorry, I'm not sure what to do about that.\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x4,basic_numbered_hour(2,x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "9dd7913d-e27e-4750-9204-6dc50b87c258"
        },
        {
            "Command": "can you show me the menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "21e7c526-6227-4537-be14-54a95bff30e7"
        },
        {
            "Command": "could you show me the menu?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "60bcfe97-9570-45f5-a87e-2abf2eb0136c"
        },
        {
            "Command": "what vegetarian dishes are there?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],_be_v_there(e2,x5))",
            "Enabled": true,
            "ID": "a62bdeda-54d0-4517-9e33-c5925a4bd1ed"
        },
        {
            "Command": "/new samples.esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "b7f0482d-eba1-4031-82c3-5692d580660d"
        },
        {
            "Command": "We want a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x14,card(2,x14,i20),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "94651de1-8fb4-409d-b16b-74193e50626d"
        },
        {
            "Command": "We'd like menus",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "15f839c0-6794-4359-b3e1-da9317c526e7"
        },
        {
            "Command": "I'd like a menu",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "943804b0-79e4-4f79-8bdd-40d9fb0642b8"
        },
        {
            "Command": "My son wants a menu",
            "Expected": "Waiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything besides a menu for you and a menu for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "fcbf99da-9fa7-4f11-8b24-02f83fd8f4b4"
        }
    ],
    "ElapsedTime": 124.61104
}