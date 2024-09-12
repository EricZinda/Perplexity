{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "69c95107-36db-4bca-b2b2-ee7d0a2a1a0e"
        },
        {
            "Command": "quit",
            "Expected": "\nThanks for playing!\nSay 'restart' to try again.",
            "Tree": "_quit_v_1(e2,i3,i4)",
            "Enabled": true,
            "ID": "97b5d5b2-03a7-462a-b939-5ffea6ef2d8e",
            "NewWorldName": "lobby"
        },
        {
            "Command": "restart",
            "Expected": "\nRestarting ...\n(Note: This game is designed to practice English: type in actual sentences you'd say in real life. If you get stuck, ask yourself what you would really say in the real world and type that.)\n\nYou\u2019re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.\nHost: Hello! How can I help you today?",
            "Tree": "_restart_v_1(e2,i3,i4)",
            "Enabled": true,
            "ID": "728a0086-364f-478d-af8f-be61bcbfb6b8",
            "NewWorldName": "esl"
        },
        {
            "Command": "/reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "353b13f3-0fed-45d1-abff-84b3c298e195"
        },
        {
            "Command": "I want a table for two",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "c4ab78f8-bc76-41e0-a786-b944006a6c92"
        },
        {
            "Command": "how much is soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),udef_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "59459548-126d-47bb-8e24-a1db2afcee0b"
        },
        {
            "Command": "I want chicken",
            "Expected": "Waiter: chicken is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you?",
            "Tree": "pronoun_q(x3,pron(x3),udef_q(x8,_chicken_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "86481953-29ab-4fdc-9ce1-1ba16215de14"
        },
        {
            "Command": "my son wants soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a chicken for you and a soup for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),udef_q(x15,_soup_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "c7cad26e-6c75-4c81-9e61-7da639e40e7e"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a chicken for you.\nWaiter: Here is a soup for Johnny.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "149ba70d-2000-48e2-b4e8-b596db95ebc7"
        },
        {
            "Command": "can I get the bill?",
            "Expected": "Waiter: Your total is 11 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i16),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "7c08c13f-cf87-4cf4-9dd3-3f6de2f50751"
        },
        {
            "Command": "cash",
            "Expected": "\nWaiter: Ah. Perfect! Have a great rest of your day.\n\nThanks for playing!\nSay 'restart' to try again.",
            "Tree": "udef_q(x4,_cash_n_1(x4),unknown(e2,x4))",
            "Enabled": true,
            "ID": "c783ebd9-c6df-4a31-a957-680bbfe53d1e",
            "NewWorldName": "lobby"
        },
        {
            "Command": "restart",
            "Expected": "\nRestarting ...\n(Note: This game is designed to practice English: type in actual sentences you'd say in real life. If you get stuck, ask yourself what you would really say in the real world and type that.)\n\nYou\u2019re going to a restaurant with your son, Johnny, who is vegetarian and too scared to order by himself. Get a table and buy lunch for both of you. You have 20 dollars in cash.\nHost: Hello! How can I help you today?",
            "Tree": "_restart_v_1(e2,i3,i4)",
            "Enabled": true,
            "ID": "e5a8ad5c-16af-4daa-9daf-fcbe3f835a31"
        }
    ],
    "ElapsedTime": 8.67467
}