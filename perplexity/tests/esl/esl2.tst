{
    "ResetModule": "esl.tutorial",
    "ResetFunction": "reset",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "0cb5995b-e3ae-44ab-93af-f94fbfc63c3a"
        },
        {
            "Command": "I want the table",
            "Expected": "There is more than 1 table",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "8a5eb15d-aec5-4844-9e37-8c9058e8e392"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9e6ae622-0ad0-4c95-bfa2-305454e96a5e"
        },
        {
            "Command": "I'd like a steak",
            "Expected": "Sorry, you must be seated to order",
            "Tree": "_a_q(x11,_steak_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "0b2e3855-cca5-4e43-8532-621909cc3094"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "4990c50f-5277-430b-9226-e1a266de9db4"
        },
        {
            "Command": "I'd like a table for 1",
            "Expected": "Johnny: Hey! That's not enough seats!",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(1,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "2f76af1e-038e-4916-b76e-a5344c2ef260"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "d5f8a208-b881-4dae-a1b6-5fdfe526a1fb"
        },
        {
            "Command": "I'd like a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(2,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "66b5319c-66be-4787-b97b-4db8ea2effe5"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "70e0d89a-bec4-40c5-858f-6e9fe40265f9"
        },
        {
            "Command": "I'd like a table for 3",
            "Expected": "Host: Sorry, we don't have a table with that many seats",
            "Tree": "_a_q(x11,udef_q(x17,[generic_entity(x17), card(3,e23,x17)],[_table_n_1(x11), _for_p(e16,x11,x17)]),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "17cdb00c-6f14-458d-a810-639281544c82"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "f3bf7412-3428-4f09-9797-bdd3982a864e"
        },
        {
            "Command": "we want a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3213c6a6-304c-488d-a079-0e91fb0cc829"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "05cf91e2-b1d4-4dc6-82b2-8614bd04382b"
        },
        {
            "Command": "My son and I want a table",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "pronoun_q(x13,pron(x13),pronoun_q(x20,pron(x20),_a_q(x25,_table_n_1(x25),udef_q(x3,def_explicit_q(x8,[_son_n_of(x8,i18), poss(e12,x8,x13)],_and_c(x3,x8,x20)),_want_v_1(e2,x3,x25)))))",
            "Enabled": true,
            "ID": "e3ce792d-b076-4fc4-b91d-7e13976d58f6"
        },
        {
            "Command": "I want a menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_menu_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "bc1ce7b9-3611-48fa-9baf-5288edde5c55"
        },
        {
            "Command": "My son wants the menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "4ecab638-357a-43e6-b768-421b52437bdb"
        },
        {
            "Command": "We would like the menus",
            "Expected": "There are less than 2 menu",
            "Tree": "_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "42d5f855-1b6d-4b48-9f8f-edecceec3774"
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
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "udef_q(x14,[generic_entity(x14), card(2,e20,x14)],pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "94651de1-8fb4-409d-b16b-74193e50626d"
        },
        {
            "Command": "We'd like menus",
            "Expected": "Waiter: Oh, I forgot to give you the menu? Here it is. The waiter walks off.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\nYou read the menu and then the waiter returns.\nWaiter: What can I get you?",
            "Tree": "udef_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "15f839c0-6794-4359-b3e1-da9317c526e7"
        },
        {
            "Command": "I'd like a menu",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "_a_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "943804b0-79e4-4f79-8bdd-40d9fb0642b8"
        },
        {
            "Command": "My son wants a menu",
            "Expected": "Oh, I already gave you a menu. You look and see that there is a menu in front of you.\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x15,_menu_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "fcbf99da-9fa7-4f11-8b24-02f83fd8f4b4"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "9e1086d8-cfd2-4762-b52d-2e421301b1da"
        },
        {
            "Command": "I want a table",
            "Expected": "How many in your party?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_table_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "048a8073-5351-43db-8e7c-b103a7722a7f"
        },
        {
            "Command": "2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there, can I get you something to eat?",
            "Tree": "udef_q(x4,[generic_entity(x4), card(2,e10,x4)],unknown(e2,x4))",
            "Enabled": true,
            "ID": "d078a2ea-e17c-44c5-9110-2600cea1e097"
        },
        {
            "Command": "I want a salad",
            "Expected": "Son: Wait, let's not order that before we know how much it costs. \nWaiter: Can I get you something to eat?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_salad_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "4ee8d866-b726-444f-9abd-ba2db97f8caf"
        },
        {
            "Command": "I would like a table",
            "Expected": "Um... You're at a table. \nWaiter: Can I get you something to eat?",
            "Tree": "_a_q(x11,_table_n_1(x11),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x11)))",
            "Enabled": true,
            "ID": "b5cfa314-b577-44c0-888c-e79450771d13"
        }
    ]
}