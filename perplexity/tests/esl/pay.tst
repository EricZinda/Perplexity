{
    "WorldName": "esl",
    "TestItems": [
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "a5589109-1dc0-4fb4-b4ee-eda0ab9ce3d9"
        },
        {
            "Command": "table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "def_implicit_q(x14,basic_numbered_hour(2,x14),pronoun_q(x3,pron(x3),_a_q(x8,[_table_n_1(x8), _for_p(e13,x8,x14)],_want_v_1(e2,x3,x8))))",
            "Enabled": true,
            "ID": "f3a009dc-1a2d-4a79-ac60-805972e7873f"
        },
        {
            "Command": "how much is soup",
            "Expected": "4 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),udef_q(x3,_soup_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "4adb123a-f0a5-47fc-8eb5-a58cf4a9cd81"
        },
        {
            "Command": "my son and I want soup",
            "Expected": "Waiter: soup is an excellent choice!\nWaiter: Can I get you anything besides a soup for Johnny and a soup for you?",
            "Tree": "pronoun_q(x13,pron(x13),pronoun_q(x20,pron(x20),udef_q(x25,_soup_n_1(x25),udef_q(x3,def_explicit_q(x8,[_son_n_of(x8,i18), poss(e12,x8,x13)],_and_c(x3,x8,x20)),_want_v_1(e2,x3,x25)))))",
            "Enabled": true,
            "ID": "f818e092-d5e9-4c93-8df6-4aa33ea933ca"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a soup for Johnny.\nWaiter: Here is a soup for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "dd9e2da0-7e00-4c07-aed9-92117eea2446"
        },
        {
            "Command": "Can we pay?",
            "Expected": "Waiter: Your total is 8 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)])",
            "Enabled": true,
            "ID": "1056e782-59cc-4f06-959a-e33ef890fc8e"
        },
        {
            "Command": "/new esl.tutorial.reset",
            "Expected": "",
            "Tree": "None",
            "Enabled": true,
            "ID": "52203d75-bc1e-4d57-98f0-3a48ce900152"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "d47e4b06-e62f-4df8-897e-15933f34821c"
        },
        {
            "Command": "can I have the menu",
            "Expected": "Waiter: Oh, I forgot to give you the menu! I'll get you one right away.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "_the_q(x11,_menu_n_1(x11),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _have_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "0103f25f-496a-4f74-a051-2c6bc984fed5"
        },
        {
            "Command": "what are your specials",
            "Expected": "Waiter: Ah, I forgot to tell you about our specials. Today we have tomato soup, green salad, and smoked pork.\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "which_q(x3,thing(x3),pronoun_q(x14,pron(x14),def_explicit_q(x8,[_special_n_1(x8), poss(e13,x8,x14)],_be_v_id(e2,x3,x8))))",
            "Enabled": true,
            "ID": "fe730c00-298a-44ce-8deb-328151b37118"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: Can I get you anything besides a menu for you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "c0e0a372-60d8-4d43-8462-550acc3ae5e2"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a menu for you and a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "563a8c08-9e38-4b8b-b057-80fd366d873a"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a menu and a steak for you and a salad for Johnny?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "23b571c9-6022-4fb7-a85c-8b693d85bf8b"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a menu and steak for you.\nWaiter: Here is a salad for Johnny.\nThe food is good, but nothing extraordinary.\n\nThe menu says:\nSteak -- $10\nRoasted Chicken -- $7\nGrilled Salmon -- $12\n\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "1261d537-a6c5-4a04-87dc-3e5552eeb4d0"
        },
        {
            "Command": "I'm ready for the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x9,_bill_n_of(x9,i14),pronoun_q(x3,pron(x3),_want_v_1(e2,x3,x9)))",
            "Enabled": true,
            "ID": "76892157-de31-423b-9717-632e623b2316"
        },
        {
            "Command": "We're ready to pay",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,i11,i12))",
            "Enabled": true,
            "ID": "6c1cee67-7ba6-49ca-9903-6c339f559e4a"
        },
        {
            "Command": "I'm ready to pay",
            "Expected": "Yes, that is true.",
            "Tree": "pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,i11,i12))",
            "Enabled": true,
            "ID": "d9151661-b0ee-4e2c-9aee-b675f4ad2dd2"
        },
        {
            "Command": "I'm ready to pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "5a8d1551-6c90-4e4a-bbe6-6a7a1ef6e477"
        },
        {
            "Command": "I'm ready to pay my son",
            "Expected": "You can't pay for that.",
            "Tree": "def_explicit_q(x11,pronoun_q(x18,pron(x18),[_son_n_of(x11,i23), poss(e17,x11,x18)]),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "75c4163a-45f2-47f4-8350-92983dccb0cf"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "f45f8cdf-ae81-4832-83a6-94041d5c09cd"
        },
        {
            "Command": "Who can pay the bill",
            "Expected": "you\n(among others)",
            "Tree": "which_q(x3,person(x3),_the_q(x11,_bill_n_of(x11,i17),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "44f9aabd-a5bf-4ccd-9020-5a7c47801c3d"
        },
        {
            "Command": "What can I pay?",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "which_q(x5,thing(x5),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x5,i16)))",
            "Enabled": true,
            "ID": "efb15731-65f2-46d7-988e-f88c537cfc2f"
        },
        {
            "Command": "I want to pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "42f554ad-0208-4bef-aad8-7171f8e5cbdd"
        },
        {
            "Command": "can I get the check?",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_check_n_of(x11,i16),pronoun_q(x3,pron(x3),[event_replace(u99,e2,e10), _get_v_1_able(e2,x3,x11)]))",
            "Enabled": true,
            "ID": "d059492d-e95d-4ec7-a6bb-15d25f2d7601"
        },
        {
            "Command": "I want to pay with a card",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e2,x14), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "5b476cfb-4422-484b-a983-61ead97e2fbe"
        },
        {
            "Command": "can I pay with a card?",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "54deedbd-3254-4d86-8f1d-6c86a4032bea"
        },
        {
            "Command": "I will pay with my card",
            "Expected": "You don't have one of those.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_card_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "5dbbce66-c57c-4e82-af30-a3db81744cde"
        },
        {
            "Command": "I want to pay the bill with a card",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i18),_a_q(x20,_card_n_1(x20),pronoun_q(x3,pron(x3),[_with_p(e19,e2,x20), _pay_v_for_request(e2,x11,i12,i13)])))",
            "Enabled": true,
            "ID": "1743ad85-9bd8-4c96-afa5-b25443b3521f"
        },
        {
            "Command": "could I pay with a card?",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "35300d37-33ae-42eb-b8c8-f6945a26647e"
        },
        {
            "Command": "I want to pay with cash",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e2,x14), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "03831612-cfaa-4d2f-b5c7-c0e6a5dfc7aa"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "0ab15121-4562-41e8-a801-ade74322a3a8"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "f8286eeb-127d-49d6-b143-e7ed95108b98"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "b32a6be3-b68b-4505-9464-4921365907a3"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "1f787d78-f9ec-4b39-bf9b-9966bb9cd689"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a salad for Johnny.\nWaiter: Here is a steak for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "79e13a5a-add9-4b25-8ab8-f63c84a5d5f2"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "6a1d167e-209a-4b8a-b9d9-589a68beaa26"
        },
        {
            "Command": "can I pay with cash?",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "e5ae3021-f61e-44c2-88c9-985e50ab51b4"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "2ce0c9fb-5ab5-4db2-aeec-759b89a62197"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "6e471301-d41c-4447-8b3e-3339dd712c26"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "2034cedd-db4a-4094-bc66-bcc7f48d3168"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ca69ff40-c67d-44e6-a758-260363757474"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a salad for Johnny.\nWaiter: Here is a steak for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "eb50592b-dcc7-4495-ba6a-1af2700f0819"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "77d7aab4-ffd2-4c67-90b3-6fcc9c0695a8"
        },
        {
            "Command": "I will pay with cash",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "udef_q(x11,_cash_n_1(x11),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "af9bf474-7a7b-43e1-a979-6773dd735457"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "56842892-f105-466b-b721-d3e9ee198978"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "42722115-fb5e-42be-9777-eb7d1fc495fb"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "b3e750e7-1d4e-446d-a518-c51b0aee5314"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "ce6eb404-69f9-4b93-a8a7-38407c16209a"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a salad for Johnny.\nWaiter: Here is a steak for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "65ef4087-be4e-4017-b18b-b346dd1e457d"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "d1cb1963-f3f3-4a4f-b6f2-b5c2ec8e72e0"
        },
        {
            "Command": "I want to pay the bill with cash",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "_the_q(x11,_bill_n_of(x11,i18),udef_q(x20,_cash_n_1(x20),pronoun_q(x3,pron(x3),[_with_p(e19,e2,x20), _pay_v_for_request(e2,x11,i12,i13)])))",
            "Enabled": true,
            "ID": "64e3beac-7292-47e7-840b-7b29471546c5"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "be37a66a-516e-4cb7-82e3-94b950c4f151"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "d61d6cd0-d604-479f-82a9-86e253eb9c86"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "98f02d54-cfbf-4f31-a3f1-bcbb4c6c13bd"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "b0326d50-039d-4531-b1df-4141c5505e27"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a salad for Johnny.\nWaiter: Here is a steak for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "9ceae3b0-240a-4245-98e7-cd76dfb02a64"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "4ca3f93b-d85b-4311-b089-a9900ee3a386"
        },
        {
            "Command": "could I pay with cash?",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "0d2939c4-874d-43a6-86ab-91767ac33a20"
        },
        {
            "Command": "a table for 2",
            "Expected": "Host: Perfect! Please come right this way. The host shows you to a wooden table with a checkered tablecloth. A minute goes by, then your waiter arrives.\nWaiter: Hi there!\nWaiter: What can I get you?",
            "Tree": "number_q(x10,card(2,x10,i16),_a_q(x4,[_table_n_1(x4), _for_p(e9,x4,x10)],unknown(e2,x4)))",
            "Enabled": true,
            "ID": "833710c0-45c2-4548-8f16-b58fff3d8b96"
        },
        {
            "Command": "how much is the salad",
            "Expected": "3 dollars\nWaiter: What can I get you?",
            "Tree": "which_q(x10,abstr_deg(x10),_the_q(x3,_salad_n_1(x3),count(e14,x10,x5,udef_q(x5,generic_entity(x5),_be_v_id(e2,x3,x5)))))",
            "Enabled": true,
            "ID": "1517b17a-adb5-4fde-b599-f6c60c2efa81"
        },
        {
            "Command": "my son wants the salad",
            "Expected": "Waiter: salad is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny?",
            "Tree": "pronoun_q(x9,pron(x9),_the_q(x15,_salad_n_1(x15),def_explicit_q(x3,[_son_n_of(x3,i14), poss(e8,x3,x9)],_want_v_1(e2,x3,x15))))",
            "Enabled": true,
            "ID": "b414bd8d-afa1-4bd1-9853-55698ecfa16c"
        },
        {
            "Command": "I want the steak",
            "Expected": "Waiter: steak is an excellent choice!\nWaiter: Can I get you anything besides a salad for Johnny and a steak for you?",
            "Tree": "pronoun_q(x3,pron(x3),_the_q(x8,_steak_n_1(x8),_want_v_1(e2,x3,x8)))",
            "Enabled": true,
            "ID": "2a14a5b6-af57-413c-81fb-cc700d4b1620"
        },
        {
            "Command": "no",
            "Expected": "Waiter: I'll be right back!\nA few minutes go by and the waiter returns.\nWaiter: Here is a salad for Johnny.\nWaiter: Here is a steak for you.\nThe food is good, but nothing extraordinary.\nWaiter: What can I get you?",
            "Tree": "_no_a_1(i6,unknown(e2,u5))",
            "Enabled": true,
            "ID": "f0771826-819a-469b-b162-9eb410d13422"
        },
        {
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "b7b72945-91ca-4ef3-b21e-e0397d50ab5f"
        },
        {
            "Command": "We'll pay with cash",
            "Expected": "Waiter: Ah. Perfect! Have a great rest of your day.\n\nYou and Johnny go back to the front of the restaurant and prepare for your next adventure!\nThere you see the friendly host ...\n\n",
            "Tree": "udef_q(x11,_cash_n_1(x11),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "5cfabc0b-2add-4936-b68d-273154204a19"
        }
    ],
    "ElapsedTime": 40.1909
}