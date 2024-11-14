{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "I want to eat a burger",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_burger_n_1(x11),pronoun_q(x3,pron(x3),_eat_v_1_request(e2,x3,x11)))",
            "Enabled": true,
            "ID": "05683e71-1eca-4fa7-89cb-d6aca79119dd"
        },
        {
            "Command": "Can I have a strawberry?",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "_a_q(x11,_strawberry_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "4f16594d-476c-4026-b82c-ea859bf4a489"
        },
        {
            "Command": "Do you have coke?",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_coke_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "f0f571f6-0201-413a-a12d-ccc0d10bb50e"
        },
        {
            "Command": "I'll take milk",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_milk_n_1(x8),_take_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "3f8d7bdb-0f04-4d10-9348-98d5c5230572"
        },
        {
            "Command": "Can I have hot sauce",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x11,[_sauce_n_1(x11), _hot_a_1(e16,x11)],pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "757ef0fd-e385-4314-915e-0a4e4754d995"
        },
        {
            "Command": "my son wants a lemonade",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x9,pron(x9),_a_q(x15,_lemonade_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "bef3d47b-f2d8-4353-a9fd-46c6c4bd9c42"
        },
        {
            "Command": "ice cream",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x10,_ice_n_1(x10),udef_q(x4,[_cream_n_1(x4), compound(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "2961cd4d-c302-41d8-84d9-264f69ad0a7b"
        },
        {
            "Command": "vegetables",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x4,_vegetable_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "25520d94-b33f-4e5a-8cd6-82b2011e94a6"
        },
        {
            "Command": "Do you have vegetables?",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_vegetable_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "daa8edf2-50aa-485f-b9a5-a37613fbae31"
        },
        {
            "Command": "I want tea",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_tea_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "9d773aa2-d575-438e-9ce8-d2c385ce18bd"
        },
        {
            "Command": "I want a burger",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_burger_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "84e97d62-1194-45c1-ade3-35bbbdf85736"
        },
        {
            "Command": "I want a tablecloth",
            "Expected": "I don't know the words: tablecloth\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_tablecloth_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "79268d62-547f-4085-8263-639aee0b52fd"
        },
        {
            "Command": "Do you have tea?",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_tea_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "a3841484-fb33-4893-9ae9-0959e1e69ba2"
        },
        {
            "Command": "Do you have a mouse?",
            "Expected": "Host: There isn't such a mouse here\nHost: How can I help you today?",
            "Tree": "pronoun_q(x3,pron(x3),_a_q(x8,_mouse_n_1(x8),_have_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ec808d20-3891-4440-aaa4-84ce92dfdc27"
        },
        {
            "Command": "tea",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x4,_tea_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "e1a2d88b-6308-4888-93d1-32d59f2f114d"
        },
        {
            "Command": "mouse",
            "Expected": "Host: Sorry, I don't think we have that here.\nHost: How can I help you today?",
            "Tree": "udef_q(x4,_mouse_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "f0d534fd-51be-4227-a571-0380025a04af"
        },
        {
            "Command": "I want a sandwich for lunch",
            "Expected": "Host: I'm sorry, you can't order that here. Take a look at the menu to see what is available.\nHost: How can I help you today?",
            "Tree": "udef_q(x14,_dish_n_of(x14),pronoun_q(x3,pron(x3),_a_q(x8,[_sandwich_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "77afc584-776a-4a60-982f-d19758609532"
        }
    ],
    "ElapsedTime": 92.19472
}