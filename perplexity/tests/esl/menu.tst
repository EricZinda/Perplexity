{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "05cf91e2-b1d4-4dc6-82b2-8614bd04382b"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),udef_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "e3ce792d-b076-4fc4-b91d-7e13976d58f6"
        },
        {
            "Command": "I want a menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "bc1ce7b9-3611-48fa-9baf-5288edde5c55"
        },
        {
            "Command": "that will be all",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for you.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "no_standalone(e2)",
            "Enabled": true,
            "ID": "4ee29d7a-4ec4-45ae-be8e-d0735a4718c2"
        },
        {
            "Command": "My son wants the menu",
            "Expected": "Waiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "4ecab638-357a-43e6-b768-421b52437bdb"
        },
        {
            "Command": "that will be all, thank you.",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the robot returns.\nWaiter: Here is a menu for Johnny.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x16,pron(x16),[no_standalone(e9)])",
            "Enabled": true,
            "ID": "3eb18b1a-240f-4fea-957b-4e9c98bcbdce"
        },
        {
            "Command": "/next_conjunct",
            "Expected": "You are welcome!  \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x16,pron(x16),[_thank_v_1(e10,x5,x16)])",
            "Enabled": true,
            "ID": "58151920-c1ae-43e1-88f7-c12df527b746"
        },
        {
            "Command": "We would like the menus",
            "Expected": "There are less than 2 menu",
            "Tree": "_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": false,
            "ID": "42d5f855-1b6d-4b48-9f8f-edecceec3774"
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
            "Expected": "I'm not sure which vegetarian menu you mean.",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,[_menu_n_1(x8), _vegetarian_a_1(e13,x8)],_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "98aa8219-aea7-4a10-a917-21bd96368a2d"
        },
        {
            "Command": "Can I see a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\n",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _see_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "ed0e789c-6ba1-4e91-98fd-a9bea2f02e27"
        },
        {
            "Command": "Do you have a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\n",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9a11bb68-b6a7-4ae5-87da-ce2853e821a9"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\n",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "22a6851e-3314-4bc9-8067-ed352aceb570"
        },
        {
            "Command": "We will see a menu",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\n",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_see_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8fd795d7-6127-4186-b87b-67680e2c551e"
        },
        {
            "Command": "Could we have a menu?",
            "Expected": "Host: Sorry, you'll need to talk to your waiter about a menu when you have a table.\n",
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
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "976df396-5503-40d5-90fe-93f121237afe"
        },
        {
            "Command": "Do you have the menu?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_menu_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "0f81d780-5bdb-4976-aae2-6144f9c6b89b"
        },
        {
            "Command": "do you have a steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "93451d18-612d-427f-bb67-ccea34c7aa58"
        },
        {
            "Command": "do you have the steak?",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ed01aa0e-79b0-4c3d-8443-f9bac852a7d4"
        },
        {
            "Command": "show me the menu",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x8,_menu_n_1(x8),pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "3abc1ec5-890e-4d20-83fd-58479d75bf6a"
        },
        {
            "Command": "show me 2 menus",
            "Expected": "Waiter: Our policy is to give one menu to every customer ... \nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "cde58b5d-7df0-4173-a792-d2379fdf4716"
        },
        {
            "Command": "show us 2 menus",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x8,[_menu_n_1(x8), card(2,e19,x8)],pronoun_q(x3,pron(x3),_show_v_1(e2,x3,x8,x9))))",
            "Enabled": true,
            "ID": "94dafbfe-00ea-4830-ab9b-e3069733741c"
        },
        {
            "Command": "that will be all, thanks",
            "Expected": "Johnny: Dad! I\u2019m vegetarian, remember?? Why did you only order meat? \nMaybe they have some other dishes that aren\u2019t on the menu? \nYou tell the waiter to ignore what you just ordered.\nWaiter: What can I get you?",
            "Tree": "_thanks_a_1(i15,no_standalone(e2))",
            "Enabled": true,
            "ID": "ec1ad85b-ce21-4f93-a7e7-c67a616fb8e8"
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
            "Expected": "you did not have 2 menu  \nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,[_menu_n_1(x8), card(2,e14,x8)],_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4dd1ccc3-2b8d-4c5e-8048-cfef07a8d1d4"
        },
        {
            "Command": "we have 3 menus",
            "Expected": "you did not have 3 menu  \nWaiter: What can I get you?",
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
            "Expected": "Host: Sorry, I don't know how to give you that.\nWaiter: What can I get you?",
            "Tree": "udef_q(x4,[generic_entity(x4), card(2,e10,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "9dd7913d-e27e-4750-9204-6dc50b87c258"
        },
        {
            "Command": "can you show me the menu?",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "21e7c526-6227-4537-be14-54a95bff30e7"
        },
        {
            "Command": "could you show me the menu?",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x12,pron(x12),_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_show_v_1_able(e2,x3,x11,x12))))",
            "Enabled": true,
            "ID": "60bcfe97-9570-45f5-a87e-2abf2eb0136c"
        },
        {
            "Command": "what vegetarian dishes are there?",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork. \nWaiter: Can I get you anything else?",
            "Tree": "_which_q(x5,[_dish_n_of(x5,i10), _vegetarian_a_1(e9,x5)],_be_v_there(e2,x5))",
            "Enabled": true,
            "ID": "a62bdeda-54d0-4517-9e33-c5925a4bd1ed"
        },
        {
            "Command": "/new esl.tutorial.reset",
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
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Oh, I forgot to give Johnny the menu! I'll get Johnny one right away.\nWaiter: Can I get you anything else?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "15f839c0-6794-4359-b3e1-da9317c526e7"
        },
        {
            "Command": "I'd like a menu",
            "Expected": "Waiter: You already ordered a menu for you\nWaiter: Can I get you anything else?",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "943804b0-79e4-4f79-8bdd-40d9fb0642b8"
        },
        {
            "Command": "My son wants a menu",
            "Expected": "Waiter: You already ordered a menu for Johnny\nWaiter: Can I get you anything else?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "fcbf99da-9fa7-4f11-8b24-02f83fd8f4b4"
        }
    ]
}