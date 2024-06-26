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
            "Command": "Can I pay the bill",
            "Expected": "Waiter: Your total is 13 dollars.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i17),pronoun_q(x3,pron(x3),_pay_v_for_request(e2,x3,x11,i12)))",
            "Enabled": true,
            "ID": "76892157-de31-423b-9717-632e623b2316"
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
            "Command": "I want to pay with cash",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e2,x14), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "03831612-cfaa-4d2f-b5c7-c0e6a5dfc7aa"
        },
        {
            "Command": "I want to pay with a card",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e2,x14), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "5b476cfb-4422-484b-a983-61ead97e2fbe"
        },
        {
            "Command": "can I pay with cash?",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "e5ae3021-f61e-44c2-88c9-985e50ab51b4"
        },
        {
            "Command": "can I pay with a card?",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "54deedbd-3254-4d86-8f1d-6c86a4032bea"
        },
        {
            "Command": "I will pay with cash",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "udef_q(x11,_cash_n_1(x11),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "af9bf474-7a7b-43e1-a979-6773dd735457"
        },
        {
            "Command": "I will pay with my card",
            "Expected": "You don't have one of those.",
            "Tree": "def_explicit_q(x11,pronoun_q(x17,pron(x17),[_card_n_1(x11), poss(e16,x11,x17)]),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "5dbbce66-c57c-4e82-af30-a3db81744cde"
        },
        {
            "Command": "I want to pay the bill with cash",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "_the_q(x11,_bill_n_of(x11,i18),udef_q(x20,_cash_n_1(x20),pronoun_q(x3,pron(x3),[_with_p(e19,e2,x20), _pay_v_for_request(e2,x11,i12,i13)])))",
            "Enabled": true,
            "ID": "64e3beac-7292-47e7-840b-7b29471546c5"
        },
        {
            "Command": "I want to pay the bill with a card",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_the_q(x11,_bill_n_of(x11,i18),_a_q(x20,_card_n_1(x20),pronoun_q(x3,pron(x3),[_with_p(e19,e2,x20), _pay_v_for_request(e2,x11,i12,i13)])))",
            "Enabled": true,
            "ID": "1743ad85-9bd8-4c96-afa5-b25443b3521f"
        },
        {
            "Command": "could I pay with cash?",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "udef_q(x14,_cash_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "0d2939c4-874d-43a6-86ab-91767ac33a20"
        },
        {
            "Command": "could I pay with a card?",
            "Expected": "You reach into your pocket and realize you don\u2019t have a credit card.\nWaiter: So, do you want to pay with cash or card?",
            "Tree": "_a_q(x14,_card_n_1(x14),pronoun_q(x3,pron(x3),[_with_p(e13,e10,x14), event_replace(u99,e2,e10), _pay_v_for_request(e2,x3,i11,i12)]))",
            "Enabled": true,
            "ID": "35300d37-33ae-42eb-b8c8-f6945a26647e"
        },
        {
            "Command": "We'll pay with cash",
            "Expected": "Ah. Perfect! Have a great rest of your day.",
            "Tree": "udef_q(x11,_cash_n_1(x11),pronoun_q(x3,pron(x3),[_with_p(e10,e2,x11), _pay_v_for(e2,x3,i8,i9)]))",
            "Enabled": true,
            "ID": "5cfabc0b-2add-4936-b68d-273154204a19"
        }
    ],
    "ElapsedTime": 10.8032
}